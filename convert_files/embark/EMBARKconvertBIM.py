"""
This script:
creates a new file with a list of SNP names to be excluded:
    SNPs on chromosome 0 (= no location available) or with a wrong location that could not be corrected
    SNPs in the SNPsToExcludeMerge.list, because of not identical snp locations between different platforms
    SNPs that are duplicate (one of the duplicate pair with the lowest call rate, or the one calling incorrect alleles)
creates a new bim file with these changes:
    SNP names in uppercase
    removes _ilmndup and _rs numbers
    adds _INDEL for SNPs with insertion or deletion
    changes indel I/D alleles to respectively A and G
    changes wrong alleles to correct alleles using EmbarkCorrectAlleles.bim
    for SNPs without or wrong location, location and chromosome is updated using EmbarkCorrectSNPPositions.map
    Change SNP id if SNP also has different id in other arrays
        (some SNPs in embark are the same as for example in Illumina array, different SNPid, but same location)
"""

import csv
import re
import time
import sys
# get the start time
st = time.time()


def split_and_strip(line, delimiter='\t'):
    """
    :param line: row of input file
    :param delimiter: the delimiter to use
    :return: stripped and split row
    """
    split_line = line.strip().split(delimiter)
    return split_line


def update_id(line, indel_snps, snps_to_exclude, dup_snps_remove):
    """
    :param line: row of input bim file
    :param indel_snps: set with SNP ids that call for indel snps
    :param snps_to_exclude: set with snps to exclude
    :param dup_snps_remove: set with duplicate snps to remove
    :return: row with the SNP id in uppercase and _ilmndup and _rsnumber removed and _INDEL added for indel snps
    """
    if line[1] in dup_snps_remove: # add _DUP to name of duplicate SNP that will be removed
        line[1] = line[1] + '_DUP'
    elif line[1] not in snps_to_exclude:
        line[1] = line[1].upper()  # line[1] is SNP id
        line[1] = re.sub("(_ILMNDUP.*|_RS.*)", "", line[1]) # remove additions to SNP name
        if line[1] in indel_snps:
            line[1] = line[1] + '_INDEL'
    return line


def get_excluded_snps_merge(file):
    """
    :param file: input file with snps to exclude when merging SNPsToExcludeMerge.list
    :return: set of SNP IDs that have to be excluded
    """
    snps_to_exclude_merge = set()
    for line in file:
        line = split_and_strip(line)
        snps_to_exclude_merge.add(line[0])
    return snps_to_exclude_merge


def get_snps_without_location(line, snps_to_exclude, count_no_correct_location):
    """
    :param line: row of input map file
    :param snps_to_exclude: set of SNP IDs that have to be excluded
    :param count_no_correct_location: counter for how many snps will be removed because location is missing
    :return: updated snps_to_exclude set with SNP ids with no position information (chromosome = 0, or basepair position = 0)
    """
    if line[0] == '0' or line[3] == '0':  # line[0] is chromosome and line[3] is basepair position of SNP on chromosome
        if line[1] not in snps_to_exclude:
            snps_to_exclude.add(line[1])
            count_no_correct_location += 1
    return snps_to_exclude, count_no_correct_location


def get_indel_snps(file):
    """
    :param file: input file with indel snp IDs
    :return: set with SNP ids that call for indel snps (allele I/D)
    """
    indel_snps = {line.strip().split("\t")[0] for line in file}
    return indel_snps


def update_alleles(line, correct_alleles, count_wrong_allele):
    """
    :param line: row of input bim file
    :param correct_alleles: dictionary with snps and their correct alleles, which have to be updated in the raw bim file
    :param count_wrong_allele: counter for how many wrong alleles were updated
    :return: row with indel alleles changed to 'fictional' alleles and with corrected alleles
    """
    # change allele I to A and D to G
    flip = str.maketrans("ID", "AG")
    line[4] = line[4].translate(flip)
    line[5] = line[5].translate(flip)
    # for snps that call wrong alleles, change these alleles
    if line[1] in correct_alleles.keys():  # line[1] is SNP id
        if line[4] not in correct_alleles[line[1]][:2] and line[4] != '0':
            line[4] = correct_alleles[line[1]][0]
            count_wrong_allele += 1
        if line[5] not in correct_alleles[line[1]][:2] and line[5] != '0':
            line[5] = correct_alleles[line[1]][0]
            count_wrong_allele += 1
    return line, count_wrong_allele


def get_id(file):
    """
    :param file: input file EmbarkSNPIdConversion
    :return: dictionary with embark ids and other platform id
    """
    different_snp_ids = {}
    for line in file:
        line = line.strip().split(",")
        different_snp_ids[line[0]] = line[1]
    return different_snp_ids


def get_correct_alleles(file):
    """
    :param file: input file with snps with correct alleles, EmbarkCorrectAlleles.bim
    :return: dictionary with format SNPid: [SNP_NEW_ALLELE1_CORRECT, SNP_NEW_ALLELE2_CORRECT, SNP_OLD_ALLELE1_WRONG,
    SNP_OLD_ALLELE2_CORRECT]
    """
    correct_alleles = {}
    for line in file:
        line = split_and_strip(line)
        correct_alleles[line[1]] = [line[4], line[5], line[6], line[7]]
    return correct_alleles


def change_id(line, different_snp_ids, count_id_changed, snps_to_exclude):
    """
    :param line: row of input bim file
    :param different_snp_ids: dictionary with embarks snp ids and corresponding other platform ids
    :param count_id_changed: counter for how many SNP ids were updated
    :param snps_to_exclude: set with snps to exclude
    :return: row with changed embark SNP id to other platforms SNP id, if SNP is in EmbarkSNPIdConversion file.
    """
    if line[1] in different_snp_ids.keys() and line[1] not in snps_to_exclude:  # line[1] is SNP id
        line[1] = different_snp_ids[line[1]]
        count_id_changed += 1
    return line, count_id_changed


def update_location(line, correct_location_snps, snps_to_exclude, snps_to_exclude_merge, count_locations_changed, count_no_correct_location):
    """
    :param line: row of input bim file
    :param correct_location_snps: dictionary with correct snps locations
    :param snps_to_exclude: set with snps to exclude
    :param snps_to_exclude_merge: set with snps to exclude when merging files
    :param count_locations_changed: number count of how many locations were wrong in original file and are changed
    :param count_no_correct_location: number count of snps with a wrong location and no correct location is available
    :return: row with updated snp location, and counts of how many locations were changed,
    and for how many snps no correct locations is available
    """
    if line[1] in snps_to_exclude_merge:
            if line[1] not in snps_to_exclude:
                snps_to_exclude.add(line[1])
                count_no_correct_location += 1
    # Check if snp is in dictionary with correct snp info
    elif line[1] in correct_location_snps.keys():  # line[1] is SNP id
        # count the number of snps that were changed
        if line[3] != correct_location_snps[line[1]][1]:  # line[3] is basepair position of SNP
            count_locations_changed += 1
        # update location
        line[0] = correct_location_snps[line[1]][0]
        line[3] = correct_location_snps[line[1]][1]
    else:
        if line[1] not in snps_to_exclude:
            count_no_correct_location += 1
            snps_to_exclude.add(line[1])
    return line, snps_to_exclude, count_locations_changed, count_no_correct_location


def get_correct_locations(file):
    """
    :param file: input file EmbarkCorrectSNPPositions.map
    :return: dictionary in format SNPid: [chromosome, location]
    """
    correct_location_snps = {}
    for line in file:
        line = split_and_strip(line)
        correct_location_snps[line[1]] = [line[0], line[3]]
    return correct_location_snps


def get_dup_snps(file1, file2, snps_to_exclude):
    """
    :param file1: input file plink .vmiss file with missingness per SNP
    :param file2: input file EmbarkDuplicatesOrWrongAllele with known duplicate snps that call correct or incorrect alleles
    :param snps_to_exclude: set with snps to exclude
    """
    wrong_duplicates = set()
    for line in file2:
        line = line.strip().split(",")
        # put snps with wrong alleles in wrong_duplicates set
        if line[2].startswith('wrong'):
            wrong_duplicates.add(line[0])

    all_snps = {}
    dup_snps_remove = set()
    for line in file1:
        line = split_and_strip(line)
        if line[0] == '0' or line[1] == '0': # skip snps without location
            continue
        snp = line[0] + '_' + line[1]
        snp_name = line[2]
        if snp_name in wrong_duplicates:
            dup_snps_remove.add(snp_name)
        elif snp not in all_snps:
            all_snps[snp] = [snp_name, line[3]]
        elif snp in all_snps and snp_name not in dup_snps_remove: # check if snp is duplicate (already present in all_snps dict.)
            if int(line[3]) <= int(all_snps[snp][1]): # compare missingness between duplicate snps
                dup_snps_remove.add(all_snps[snp][0]) # add snp with highest missingness to set with dup snps to remove
            else:
                dup_snps_remove.add(snp_name)
    count_duplicates = len(dup_snps_remove)
    for snp in dup_snps_remove:
        if snp not in snps_to_exclude:  # add the duplicates that should be removed to list snps_to_exclude list
            snps_to_exclude.add(snp+'_DUP')
    return snps_to_exclude, count_duplicates, dup_snps_remove


def main():
    """ Creates a new BIM file,
    and creates a file with SNPs that have _ilmndup in SNP id,
    and creates a file with mitochondrial SNPs,
    and creates a file with SNPs to exclude,
    and creates a file with indel SNP ids
    """
    # input files
    filename_bim = sys.argv[1]  # input plink .bim file
    snps_to_exclude_merge = 'convert_files/common_files/SNPsToExcludeMerge.list'  # File with SNPids to exclude when merging files
    snp_id_conversion = 'convert_files/embark/EmbarkSNPIdConversion'  # File to use for changing SNP ids
    embark_duplicates_or_different_allele = 'convert_files/embark/EmbarkDuplicatesOrWrongAllele'  # File with duplicate snps
    embark_correct_locations = 'convert_files/embark/EmbarkCorrectSNPPositions.map'
    embark_correct_alleles = 'convert_files/embark/EmbarkCorrectAlleles.bim'
    filename_indels = 'convert_files/embark/EmbarkIndelSNPs.txt'
    embark_missingness_per_snp = sys.argv[2]

    # Output files
    new_filename_bim = sys.argv[4]
    embark_snps_to_exclude = sys.argv[3]  # File with SNPnames to use in --exclude plink

    with open(filename_bim, mode="r") as DataBIM, \
            open(snps_to_exclude_merge, mode="r") as DataExcludeMerge, \
            open(embark_duplicates_or_different_allele, mode="r") as DataUnusualSNPs, \
            open(embark_correct_locations, mode="r") as DataCorrectLocations, \
            open(new_filename_bim, "w", newline='') as NewFileBIM, \
            open(embark_snps_to_exclude, "w", newline='') as NewFileExcludedSNPs, \
            open(filename_indels, mode="r") as DataIndels, \
            open(snp_id_conversion, mode="r") as DataSNPID, \
            open(embark_correct_alleles, mode="r") as DataCorrectAlleles, \
            open(embark_missingness_per_snp, mode="r") as Missingness_snp:
        writer_exclude = csv.writer(NewFileExcludedSNPs, delimiter='\t')
        writer_bim = csv.writer(NewFileBIM, delimiter='\t')

        snps_to_exclude = set()
        count_locations_changed = 0
        count_no_correct_location = 0
        count_wrong_allele = 0
        count_id_changed = 0

        indel_snps = get_indel_snps(DataIndels)  # Get set of indel snps

        # Get snps from SNPsToExcludeMerge.list
        snps_to_exclude_merge = get_excluded_snps_merge(DataExcludeMerge)

        # Get set of duplicate snps to remove
        snps_to_exclude,count_duplicates,dup_snps_remove = get_dup_snps(Missingness_snp, DataUnusualSNPs, snps_to_exclude)

        # Get dictionary of embark SNP ids with different id in other array, and corresponding other platform ids
        different_snp_ids = get_id(DataSNPID)

        # Get dictionary of SNPs with their correct alleles
        correct_alleles = get_correct_alleles(DataCorrectAlleles)

        # Get dictionary of the correct locations of SNPs
        correct_location_snps = get_correct_locations(DataCorrectLocations)

        # create a new bim file, and add snps to Embarks snps to exclude file
        for line in DataBIM:
            line = split_and_strip(line)
            # Make all snp ids uppercase, remove _ilmndup1 and _rsnumber from SNP id and add _INDEL to indels snps
            line = update_id(line, indel_snps, snps_to_exclude, dup_snps_remove)
            # Change SNP id for Embark SNPs that have different name in other platform arrays
            line, count_id_changed = change_id(line, different_snp_ids, count_id_changed, snps_to_exclude)
            # Update locations and count how many snp locations were changed, and of how many snps no correct location
            # is available (these snps are put in snps_to_exclude set).
            line, snps_to_exclude, count_locations_changed, count_no_correct_location \
                = update_location(line, correct_location_snps, snps_to_exclude, snps_to_exclude_merge, count_locations_changed,
                               count_no_correct_location)
            # update wrong alleles to correct alleles and change indel alleles (I=A, D=G)
            line, count_wrong_allele = update_alleles(line, correct_alleles, count_wrong_allele)
            # Write adjusted row to new bim file
            writer_bim.writerow(line)
            # Add snps with chromosome 0 or position 0 to embarks snps to exclude set
            snps_to_exclude, count_no_correct_location = get_snps_without_location(line, snps_to_exclude, count_no_correct_location)

        # Write snps to exclude to new file
        for snp in snps_to_exclude:
            writer_exclude.writerow([snp])

        print("Number of SNPs to be deleted: ", len(snps_to_exclude))
        print("\t- Number of SNPs of which no correct location is available, or location differs between arrays: ", count_no_correct_location)
        print("\t- Number of duplicate SNPs: ", count_duplicates)
        print("Number of SNPs of which location is updated: ", count_locations_changed)
        print("Number of SNPs for which alleles were corrected: ", count_wrong_allele)
        print("Number of SNPs of which id is updated: ", count_id_changed)


main()

# get the end time
et = time.time()

# get the execution time
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')
