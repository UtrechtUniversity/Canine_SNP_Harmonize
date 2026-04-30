"""
This script:
Creates a new MAP file, with the following changes:
    SNP names to uppercase
    RS number removed from SNPname
    X chromosome divided over chromosome 41 (pseudo-autosomal) and 39
Creates a new PED file with the following changes:
    0-1-2 allele coding of wisdom is converted to ACTG forward
    missing alleles (-1) are changed to 0
Creates a file with SNPs to use in --exclude in plink
    SNPs without location (chromosome = 0)
    SNPs not in translation table
    SNPs that call wrong alleles
"""
import pandas as pd
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


def get_translation_info(file):
    """
    :param file: input file (translation table file)
    :return: dictionary of snps in translation table (snp_id: [alleles0, alleles1, alleles2])
    """
    translation_snp_info = {}
    for index, line in enumerate(file):
        if index == 0:
            continue
        line = split_and_strip(line)
        translation_snp_info[line[0]] = [line[1], line[2], line[3]]
    return translation_snp_info


def update_chromosome(line):
    """
    :param line: input row
    :return: row with updated chromosome (X divided over 39 and 41 (pseudo-autosomal), and Y/X changed to 0)
    """
    if line.iloc[1] == 'X':  # line.iloc[1] is chromosome, line.iloc[2] is basepair position
        if int(line.iloc[2]) < 6640000:
            # for SNPs in the pseudo autosomal region, change chromosome X to 41
            line.iloc[1] = '41'
        else:
            # for SNPs NOT in the pseudo autosomal region, change chromosome X to 39
            line.iloc[1] = '39'
    if line.iloc[1] == 'Y/X' or line.iloc[1] == 'XY':
        line.iloc[1] = '0'

    return line


def update_id(line):
    """
    :param line: row of input map file
    :return: row with SNP id without _rsnumber
    """
    line.iloc[0] = re.sub("(_rs.*)", "", line.iloc[0]).upper()
    return line


def get_sample_ids(file):
    """
    :param file: input file
    :return: list with sample ids (are the column names)
    """
    sample_ids = list(file.columns)
    sample_ids = sample_ids[3:]
    return sample_ids


def get_sample_info(sample):
    """
    :param sample: input sample
    :return: a list with info of the sample: family ID, individual ID, Paternal Id, Maternal Id, Sex, Phenotype,
    of which the last 4 are set to 0
    """
    sample_info = [sample, sample, "0", "0", "0", "0"]
    return sample_info


def get_alleles(data, sample, sample_info, translation_snp_info):
    """
    :param data: input data
    :param sample: current sample
    :param sample_info: list with family ID, individual ID, Paternal Id, Maternal Id, Sex, Phenotype
    :param translation_snp_info: dictionary with snp info of snps in translation table
    :return: sample_info list with added alleles in ACTG format
    """
    column = data[sample]
    for index, SNP in enumerate(column):
        SNP_id = re.sub("(_rs.*)", "", data.iloc[index, 0]).upper()
        # if allele is coded as -1 (missing), change this to 0 0
        if SNP == -1:
            sample_info += ['0', '0']

        # change non-missing alleles
        elif SNP_id in translation_snp_info.keys():
            # translate allele 0
            if SNP == 0:
                allele1 = re.findall('(.) ', translation_snp_info[SNP_id][0])
                allele2 = re.findall(' (.)', translation_snp_info[SNP_id][0])
                sample_info += allele1 + allele2
            # translate allele 1
            if SNP == 1:
                allele1 = re.findall('(.) ', translation_snp_info[SNP_id][1])
                allele2 = re.findall(' (.)', translation_snp_info[SNP_id][1])
                sample_info += allele1 + allele2
            # translate allele 2
            if SNP == 2:
                allele1 = re.findall('(.) ', translation_snp_info[SNP_id][2])
                allele2 = re.findall(' (.)', translation_snp_info[SNP_id][2])
                sample_info += allele1 + allele2
        elif SNP_id not in translation_snp_info.keys():
            sample_info += ['0', '0']
    return sample_info


def get_snps_to_exclude(line, snps_to_exclude, snps_exclude_merge, snps_exclude_incorrect_alleles, translation_snp_info, count_no_correct_location, count_not_in_snptable, count_exclude_merge, count_snps_incorrect_alleles):
    """
    :param line: input row
    :param snps_to_exclude: set with snps to exclude, to which to append new snps
    :param snps_exclude_merge: list with snps that have a different location between arrays
    :param snps_exclude_incorrect_alleles: list with snps that have incorrect alleles
    :param translation_snp_info: dictionary with snp info translation table
    :param count_no_correct_location: counter for how many snps have no location
    :param count_not_in_snptable: counter for how many snps are not in snptable, so no alleles known
    :param count_exclude_merge: counter for how many snps have different locations between arrays
    :param count_snps_incorrect_alleles: counter for how many snps have incorrect alleles
    :return: list with snps that have to be excluded
    """
    # for snps that have different location between arrays, add them to exclude list and count them
    if line.iloc[0] in snps_exclude_merge:
        if line.iloc[0] not in snps_to_exclude:
            snps_to_exclude.add(line.iloc[0])
            count_exclude_merge += 1
    # for snps that call wrong alleles, add them to exclude list and count them
    if line.iloc[0] in snps_exclude_incorrect_alleles:
        if line.iloc[0] not in snps_to_exclude:
            snps_to_exclude.add(line.iloc[0])
            count_snps_incorrect_alleles += 1
    # for snps without a known correct location, add them to exclude list and count them
    if line.iloc[1] == '0' or line.iloc[1] == 'Y/X':
        if line.iloc[0] not in snps_to_exclude:
            snps_to_exclude.add(line.iloc[0])
            count_no_correct_location += 1
    # for snps not present in SNP table, add them to exclude list and count them
    if line.iloc[0] not in translation_snp_info.keys() and line.iloc[0] not in snps_to_exclude:
        snps_to_exclude.add(line.iloc[0])
        count_not_in_snptable += 1
    return snps_to_exclude, count_no_correct_location, count_not_in_snptable, count_exclude_merge, count_snps_incorrect_alleles


def get_snps(file):
    """
    :param file: input file
    :return: list with snps present in input file
    """
    snps = set()
    for line in file:
        split_line = line.strip()
        snps.add(split_line)
    return snps


def main():
    """
    Creates a new map and ped file, and a file with snps to exclude.
    """
    # input files
    inputfile = sys.argv[1]  # input .xlsx file
    translation_table = 'convert_files/wisdom/WisdomTranslationTable.txt'
    snps_to_exclude_merge = 'convert_files/common_files/SNPsToExcludeMerge.list'  # file with SNPids to exclude when merging files
    snps_with_incorrect_alleles = 'convert_files/wisdom/Wisdom_incorrect_alleles.txt'

    # output files
    snps_to_exclude = sys.argv[2]
    new_filename_map = sys.argv[3] + '.map'
    new_filename_ped = sys.argv[3] + '.ped'

    with (open(inputfile, mode="rb") as Data, \
            open(translation_table, mode="r") as DataTranslation, \
            open(snps_to_exclude_merge, mode="r") as DataExcludeMerge, \
            open(snps_with_incorrect_alleles, mode="r") as DataIncorrectAlleles, \
            open(new_filename_map, "w", newline='') as NewFileMAP, \
            open(snps_to_exclude, "w", newline='') as NewFileExcludedSNPs, \
            open(new_filename_ped, "w", newline='') as NewFilePED):
        writer_map = csv.writer(NewFileMAP, delimiter='\t')
        writer_ped = csv.writer(NewFilePED, delimiter='\t')
        writer_exclude = csv.writer(NewFileExcludedSNPs, delimiter='\t')

        data = pd.read_excel(Data, header=0)
        # make sets of SNPs present in input files
        snps_exclude_merge = get_snps(DataExcludeMerge)
        snps_exclude_incorrect_alleles = get_snps(DataIncorrectAlleles)

        # make dictionary of SNPs in translation table
        translation_snp_info = get_translation_info(DataTranslation)

        count_no_correct_location = 0
        count_not_in_snptable = 0
        count_exclude_merge = 0
        count_snps_incorrect_alleles = 0

        # make list with sample ids
        sample_ids = get_sample_ids(data)
        snps_to_exclude = set()
        # make map file
        for index, line in data.iterrows():
            line = update_chromosome(line)
            line = update_id(line)
            # check if snps needs to be excluded
            snps_to_exclude, count_no_correct_location, count_not_in_snptable, count_exclude_merge, \
            count_snps_incorrect_alleles \
            = get_snps_to_exclude(line, snps_to_exclude, snps_exclude_merge, snps_exclude_incorrect_alleles,
                                  translation_snp_info, count_no_correct_location, count_not_in_snptable,
                                  count_exclude_merge, count_snps_incorrect_alleles)
            line_map = [str(line.iloc[1]), str(line.iloc[0]), '0', str(line.iloc[2])]
            writer_map.writerow(line_map)

        for snp in snps_to_exclude:
            writer_exclude.writerow([snp])

        # make ped file
        for index, sample in enumerate(sample_ids):
            # get Family id, sample id and 4 zeros
            sample_info = get_sample_info(sample)
            # add alleles to the sample info
            sample_info = get_alleles(data, sample, sample_info, translation_snp_info)
            writer_ped.writerow(sample_info)

        print("Number of SNPs to be deleted: ", len(snps_to_exclude))
        print("\t- Number of SNPs of which no correct location is available, or location differs between arrays: ",
              count_no_correct_location + count_exclude_merge)
        print("\t- Number of SNPs not present in translation table (so alleles are unknown): ", count_not_in_snptable)
        print("\t- Number of SNPs that call incorrect alleles: ", count_snps_incorrect_alleles)


main()


# get the end time
et = time.time()

# get the execution time
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')