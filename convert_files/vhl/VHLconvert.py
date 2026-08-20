"""
This script:
creates a new file with a list of SNP names to be excluded:
    SNPs on chromosome 0 (= no location available) or location 0
    SNPs without known correct alleles, or known incorrect alleles
    SNPs in the SNPsToExcludeMerge.list, because of not identical snp locations between different platforms
creates a new bim file with these changes:
    Change SNP id if SNP also has different id in other arrays
        if this is not true, add _VHL behind the snp ID
    Changes chromosome coding:
        for SNPs in the pseudo autosomal region, change chromosome 39 to 41
    Changes indel I/D alleles to respectively A and G
"""

import csv
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


def get_excluded_snps_merge(file, snp_ids_alleles):
    """
    :param file: input file with snps to exclude when merging SNPsToExcludeMerge.list
    :param snp_ids_alleles: dictionary of each SNP with updated ID and correct alleles
    :return: set of SNP IDs that have to be excluded
    """
    snps_to_exclude_merge = set()
    for line in file:
        line = split_and_strip(line)
        snps_to_exclude_merge.add(line[0])
    for snp in snp_ids_alleles.keys(): # get original ID names to add to the list of snps to exclude
        if snp_ids_alleles[snp][0] in snps_to_exclude_merge:
            snps_to_exclude_merge.add(snp)
    return snps_to_exclude_merge


def get_snps_without_location(line, snps_to_exclude, snps_to_exclude_merge, count_no_correct_location):
    """
    :param line: row of input map file
    :param snps_to_exclude: set of SNP IDs that have to be excluded
    :param snps_to_exclude_merge: set of SNP IDs that have to be excluded when merging files
    :param count_no_correct_location: counter for how many snps will be removed because location is missing
    :return: updated snps_to_exclude set with SNP ids with no chromosome information (chromosome = 0, or position = 0)
    """
    if line[0] == '0' or line[3] == '0':  # line[0] is chromosome and line[3] is basepair position of SNP on chromosome
        if line[1] not in snps_to_exclude:
            snps_to_exclude.add(line[1])
            count_no_correct_location += 1
    elif line[1] in snps_to_exclude_merge:
        if line[1] not in snps_to_exclude:
            snps_to_exclude.add(line[1])
            count_no_correct_location += 1
    return snps_to_exclude, count_no_correct_location

def update_chromosome(line):
    """
    :param line: row of snp map file
    :return: row with updated chromosome: X chromosomes divided over 39 en 41 (pseudo-autosomal), and Y becomes 40
    """
    if line[0] == '39':  # line[0] is chromosome
        if int(line[3]) < 6640000:  # line[3] is basepair position
            # For SNPs in the pseudo autosomal region, change chromosome X to 41
            line[0] = '41'
        else:
            # For SNPs NOT in the pseudo autosomal region, change chromosome X to 39
            line[0] = '39'
    return line


def check_alleles_and_loc(line, snp_ids_alleles, count_wrong_allele, snps_to_exclude, count_locations_changed):
    """
    :param line: row of input bim file
    :param snp_ids_alleles: dictionary with snps and new ID and their correct alleles, which have to be updated in the raw bim file
    :param count_wrong_allele: counter for how many wrong alleles were updated
    :param snps_to_exclude: set of SNP IDs that have to be excluded
    :param count_locations_changed: counter for how many locations were changed
    :return: row with corrected alleles and location, updated snps_to_exclude set with SNPs with wrong alleles
    """
    # change allele I to A and D to G
    flip = str.maketrans("ID", "AG")
    line[4] = line[4].translate(flip)
    line[5] = line[5].translate(flip)
    # check if alleles are correct, using dictionary with correct alleles per snp
    # for snps that call wrong alleles, add those to the list with snps to exclude
    if line[1] in snp_ids_alleles.keys():  # line[1] is SNP id
        # check location
        if line[0] != snp_ids_alleles[line[1]][1] or line[3] != snp_ids_alleles[line[1]][2]:
            line[0] = snp_ids_alleles[line[1]][1] # update chromosome
            line[3] = snp_ids_alleles[line[1]][2] # update location
            count_locations_changed += 1

        # check alleles
        if line[4] not in snp_ids_alleles[line[1]][3:] and line[4] != '0': # line[4] is allele1
            if line[1] not in snps_to_exclude:
                snps_to_exclude.add(line[1])
                count_wrong_allele += 1
        if line[5] not in snp_ids_alleles[line[1]][3:] and line[5] != '0': # line[5] is allele2
            if line[1] not in snps_to_exclude:
                snps_to_exclude.add(line[1])
                count_wrong_allele += 1

        # if allele = 0 (not known, because it is missing in all animals), update this allele to the known allele for this SNP
        elif line[4] == '0' and line[5] == '0':
            line[4] = snp_ids_alleles[line[1]][3]
            line[5] = snp_ids_alleles[line[1]][4]
        elif line[4] == '0':
            if line[5] == snp_ids_alleles[line[1]][3]:
                line[4] = snp_ids_alleles[line[1]][4]
            elif line[5] == snp_ids_alleles[line[1]][4]:
                line[4] = snp_ids_alleles[line[1]][3]
        elif line[5] == '0':
            if line[4] == snp_ids_alleles[line[1]][3]:
                line[5] = snp_ids_alleles[line[1]][4]
            elif line[4] == snp_ids_alleles[line[1]][4]:
                line[5] = snp_ids_alleles[line[1]][3]
    else:
        if line[1] not in snps_to_exclude and line[0] != '0' and line[3] != '0':
            snps_to_exclude.add(line[1])
            count_wrong_allele += 1
    return line, count_wrong_allele, snps_to_exclude, count_locations_changed


def get_id_and_correct_alleles(file):
    """
    :param file: input file VHL_snp_info.txt
    :return: dictionary with vhl ids and other platform id, and the correct alleles
    """
    snp_ids_alleles = {}
    for line in file:
        line = split_and_strip(line)
        snp_ids_alleles[line[2]] = [line[3], line[0], line[1], line[4], line[5]] # vhl_id = [new_id, chromosome, location, allele1, allele2]
    return snp_ids_alleles

def change_id(line, snp_ids_alleles, count_id_changed, dup_snps_remove):
    """
    :param line: row of input bim file
    :param snp_ids_alleles: dictionary with vhl snp ids and corresponding other platform ids
    :param count_id_changed: counter for how many SNP ids were updated
    :param dup_snps_remove: set with duplicate snps to remove
    :return: row with changed vhl SNP id to other platforms SNP id (using VHL_snp_info.txt)
    """

    if line[1] in dup_snps_remove: # add _DUP to name of duplicate SNP that will be removed
        line[1] = line[1] + '_DUP'
    elif line[1] in snp_ids_alleles.keys():  # line[1] is SNP id
        if line[1] != snp_ids_alleles[line[1]][0]: # check if there is an new SNPid available for the VHL snp
            count_id_changed += 1
            line[1] = snp_ids_alleles[line[1]][0]  # change SNP id to new SNPid
    return line, count_id_changed

def get_dup_snps(file1, snps_to_exclude):
    """
    :param file1: input file plink .vmiss file with missingness per SNP
    :param snps_to_exclude: set with snps to exclude
    """

    all_snps = {}
    dup_snps_remove = set()
    for line in file1:
        line = split_and_strip(line)
        line[2] = line[2] + '_VHL'
        if line[0] == '0' or line[1] == '0': # skip snps without location
            continue
        snp = line[0] + '_' + line[1]
        snp_name = line[2]
        if snp not in all_snps:
            all_snps[snp] = [snp_name, line[3]]
        elif snp in all_snps and snp_name not in dup_snps_remove: # check if snp is duplicate (already present in all_snps dict.)
            if int(line[3]) <= int(all_snps[snp][1]): # compare missingness between duplicate snps
                dup_snps_remove.add(all_snps[snp][0]) # add snp with highest missingness to set with dup snps to remove
                all_snps[snp] = [snp_name, line[3]]
            else:
                dup_snps_remove.add(snp_name)
    count_duplicates = len(dup_snps_remove)
    for snp in dup_snps_remove:
        if snp not in snps_to_exclude:  # add the duplicates that should be removed to list snps_to_exclude list
            snps_to_exclude.add(snp+'_DUP')
    return snps_to_exclude, count_duplicates, dup_snps_remove


def main():
    """ Creates a new BIM file,
    and creates a file with SNPs to exclude
    """
    # input files
    filename_bim = sys.argv[1]  # input plink .bim file
    snps_to_exclude_merge = 'convert_files/common_files/SNPsToExcludeMerge.list'  # File with SNPids to exclude when merging files
    snp_info = 'convert_files/vhl/VHL_snp_info.txt' # File with correct alleles and SNP ids from other arrays
    missingness_per_snp = sys.argv[2]

    # Output files
    new_filename_bim = sys.argv[4]
    vhl_snps_to_exclude = sys.argv[3]  # File with SNPnames to use in --exclude plink

    with open(filename_bim, mode="r") as DataBIM, \
            open(snps_to_exclude_merge, mode="r") as DataExcludeMerge, \
            open(snp_info, mode="r") as snp_info, \
            open(new_filename_bim, "w", newline='') as NewFileBIM, \
            open(vhl_snps_to_exclude, "w", newline='') as NewFileExcludedSNPs, \
            open(missingness_per_snp, mode="r") as Missingness_snp:
        writer_exclude = csv.writer(NewFileExcludedSNPs, delimiter='\t')
        writer_bim = csv.writer(NewFileBIM, delimiter='\t')

        snps_to_exclude = set()
        count_no_correct_location = 0
        count_locations_changed = 0
        count_wrong_allele = 0
        count_id_changed = 0

        # Get set of duplicate snps to remove
        snps_to_exclude, count_duplicates, dup_snps_remove = get_dup_snps(Missingness_snp, snps_to_exclude)

        # Get dictionary of vhl SNP ids with different id in other array, and corresponding other platform ids,
        # and the correct alleles
        snp_ids_alleles = get_id_and_correct_alleles(snp_info)

        # Get snps from SNPsToExcludeMerge.list
        snps_to_exclude_merge = get_excluded_snps_merge(DataExcludeMerge, snp_ids_alleles)

        # create a new bim file, and add snps to VHLs snps to exclude file
        for line in DataBIM:
            line = split_and_strip(line)
            line[1] = line[1] + '_VHL'
            # Add snps with chromosome 0 or position 0 to VHLs snps to exclude set
            snps_to_exclude, count_no_correct_location = get_snps_without_location(line, snps_to_exclude, snps_to_exclude_merge, count_no_correct_location)
            # change chromosome coding: 39 to 39 or 41 (pseudo-autosomal)
            line = update_chromosome(line)
            # check for wrong alleles and location
            line, count_wrong_allele, snps_to_exclude, count_locations_changed = check_alleles_and_loc(line, snp_ids_alleles, count_wrong_allele, snps_to_exclude, count_locations_changed)
            # Change SNP id for VHL SNPs that have different name in other platform arrays
            line, count_id_changed = change_id(line, snp_ids_alleles, count_id_changed, dup_snps_remove)
            # Write adjusted row to new bim file
            writer_bim.writerow(line)


        # Write snps to exclude to new file
        for snp in snps_to_exclude:
            writer_exclude.writerow([snp])

        print("Number of SNPs to be deleted: ", len(snps_to_exclude))
        print("\t- Number of SNPs of which no correct location is available, or location differs between arrays: ", count_no_correct_location)
        print("\t- Number of SNPs for which correct alleles are unknown: ", count_wrong_allele)
        print("\t- Number of duplicate SNPs: ", count_duplicates)
        print("Number of SNPs of which location is updated: ", count_locations_changed)
        print("Number of SNPs of which id is updated: ", count_id_changed)


main()

# get the end time
et = time.time()

# get the execution time
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')
