"""
This script:
Creates a new pvar file with these changes:
    adds SNP id for known snps, based on base pair position
    SNPs on chromosome 39 are divided over 39 and 41 (pseudo-autosomal)
    flipped strands when needed
    changes alleles of indel IDs to fictional alleles A (insertion) and G (deletion)
Creates a file with SNPs to extract
    only snps:
        with a SNP id
        bi-allelic
        with alleles matching known SNP alleles
"""

import csv
import time
import sys
import re
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


def get_snp_info(file):
    """
    :param file: input file with correct locations and alleles in forward
    :return: dictionary with format ('location:chromosome': 'SNP id') and dictionary with format ('snp id': [allele 1, allele 2]
    """
    snp_info = {}
    forward_alleles = {}
    for line in file:
        line = split_and_strip(line)
        snp_info[line[1] + ':' + line[2]] = line[0]
        forward_alleles[line[0]] = [line[3], line[4]]
    return snp_info, forward_alleles


def get_snp_name_and_update_chromosome(line, snp_info, count_snp_id_not_found):
    """
    :param line: input row of pvar file
    :param snp_info: dictionary with snp information in format ('location:chromosome': 'SNP id')
    :param count_snp_id_not_found: counter for how many snps miss a snp id
    :return: row with updated chromosome (chr 39 divided over 39 and 41 = pseudo-autosomal), added SNP id when location
    and chromosome combination match with a SNP in snp_info dictionary, and updated alleles for indel snps (insertion
    becomes A, deletion becomes G). Changed SNP_id to '.' when non-indel SNPs code for indels, and when a * is present
    in the alleles (‘*’ indicates that the allele is missing due to a upstream deletion).
    """
    # divide chr 39 over 39 and 41 (pseudo-autosomal)
    if line[0].startswith('chr'):
        line[0] = re.sub("chr", '', line[0])
    if line[0] == '39' or line[0] == '41' or line[0] == 'X':
        if int(line[1]) < 6640000:
            line[0] = '41'
        else:
            line[0] = '39'
    elif line[0] == 'Y':
        line[0] = '40'
    elif line[0] == 'MT':
        line[0] = '42'
    loc = line[0] + ':' + line[1]
    # if chromosome-location combination is in the snp_info dictionary, get corresponding SNP id from dictionary
    if loc in snp_info.keys():
        line[2] = snp_info[loc]
        # if snp was found, delete this snp from dictionary, so no duplicate SNPs end up in pvar file
        # (second snp of duplicate gets '.' for snp id).
        del snp_info[loc]
    else:
        line[2] = '.'
        count_snp_id_not_found += 1
    return line, count_snp_id_not_found



def update_alleles(line, forward_alleles, count_flip, count_tri_allelic):
    """
    :param line: input row of pvar file
    :param forward_alleles: dictionary with forward alleles for each SNP
    :param count_flip: number count for flipped strands
    :param count_tri_allelic: number count for triallelic SNPs
    :return: updated row (with flipped strand if necessary, and SNP id is changed to '.' for SNPs that call wrong,
    (tri-)allelic alleles (they do not match with alleles in forward_alleles dictionary)), the number count for flipped
    strands and tri-allelic/wrong alleles.
    """
    # line[2] is SNP id, line[3] and [4] are ref and alt alleles
    if line[2] != '.' and line[2] in forward_alleles.keys():
        # get correct forward alleles for this SNP
        correct_alleles = forward_alleles[line[2]]
        if ',' in line[3] or ',' in line[4] or '*' in line[3] or '*' in line[4]:
            line[2] = '.'
        # if alleles in pvar file are not the same as correct forward alleles, flip strand
        elif line[3] not in correct_alleles or line[4] not in correct_alleles:
            flip = str.maketrans("ATCG", "TAGC")
            line[3] = line[3].translate(flip)
            line[4] = line[4].translate(flip)
            # check if alleles are now correct after flipping strand
            if line[3] in correct_alleles and line[4] in correct_alleles:
                count_flip += 1
            # if alleles are still not the same as correct forward alleles, change SNP id to '.'
            if line[3] not in correct_alleles or line[4] not in correct_alleles:
                count_tri_allelic += 1
                line[2] = '.'
        if line[2].endswith('_INDEL'):  # line[2] is SNP id
            if len(line[3]) > len(line[4]):
                line[3] = 'A' # insertion
                line[4] = 'G' # deletion
            else:
                line[3] = 'G' # deletion
                line[4] = 'A' # insertion
    else:
        line[2] = '.'
    return line, count_flip, count_tri_allelic


def get_snps_to_extract(line, snps_to_extract, count_kept, count_removed):
    """
    :param line: input row of pvar file
    :param snps_to_extract: list with SNPs that should be extracted (are correct SNPs with a SNP id, not '.')
    :param count_kept: number count of extracted SNPs
    :param count_removed: number count of SNPs that will not be extracted, and thus removed
    :return: updated list with SNPs to extract, number count of SNPs to extract and to remove
    """
    if line[2] != '.':  # line[2] is SNP id
        snps_to_extract.append(line[2])
        count_kept += 1
    if line[2] == '.':
        count_removed += 1
    return snps_to_extract, count_kept, count_removed


def main():
    """"
    Creates a new pvar file and a SNPSToExtract list file to use in plink --extract
    """

    # input files
    filename_pvar = sys.argv[1]  # input plink .pvar file
    filename_forward_snps = 'convert_files/common_files/SNPs_forward_alleles.txt'

    # output files
    newfile_pvar = sys.argv[2] + '.pvar'
    snps_to_extract = sys.argv[2] + '_extract.list'

    with open(filename_pvar, mode="r") as DataPVAR, \
            open(filename_forward_snps, mode="r") as DataForwardSNPs, \
            open(newfile_pvar, "w", newline='') as NewFilePVAR, \
            open(snps_to_extract, "w", newline='') as NewFileExtractedSNPs:
        writer_extract = csv.writer(NewFileExtractedSNPs, delimiter='\t')
        writer_pvar = csv.writer(NewFilePVAR, delimiter='\t')

        # get dictionary of known SNPs and a dictionary of their forward alleles
        snp_info, forward_alleles = get_snp_info(DataForwardSNPs)

        count_flip, count_tri_allelic, count_removed, count_kept, count_snp_id_not_found = 0, 0, 0, 0, 0

        snps_to_extract = []
        writer_pvar.writerow(['#CHROM', 'POS', 'ID', 'REF', 'ALT'])
        for line in DataPVAR:
            if line.startswith('#'):
                continue
            line = split_and_strip(line)
            # add SNP id to known SNPs and divide chromosome 39 over 39 and 41 (pseudo-autosomal)
            line, count_snp_id_not_found = get_snp_name_and_update_chromosome(line, snp_info, count_snp_id_not_found)
            # update alleles, flip strand when necessary
            line, count_flip, count_tri_allelic = update_alleles(line, forward_alleles, count_flip, count_tri_allelic)
            snps_to_extract, count_kept, count_removed = get_snps_to_extract(line, snps_to_extract,
                                                                             count_kept, count_removed)
            writer_pvar.writerow(line)

        for snp in snps_to_extract:
            writer_extract.writerow([snp])

        print('Number of strand flips:', count_flip)
        print('Number of SNPs calling alleles not matching SNP database (tri-allelic):', count_tri_allelic)
        print('Number of snps for which no SNP id was found:', count_snp_id_not_found)
        print('Number of snps to remove (tri-allelic snps + no SNP-id found):', count_removed)
        print('Number of correct snps:', count_kept)


main()


# get the end time
et = time.time()

# get the execution time
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')