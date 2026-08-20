"""
This script:
Creates a new pvar file with these changes:
    adds SNP id for known snps, based on base pair position
    SNPs on chromosome 39 are divided over 39 and 41 (pseudo-autosomal)
    flipped strands when needed
    changes alleles of indel IDs to fictional alleles A (insertion) and G (deletion)
    changes locations from canfam 4 to 3
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
    :param file: input file with correct alleles in forward CF4 and locations in CF3 and CF4
    :return: dictionary with format ('chromCF4_locationCF4': [SNPid, chromCF3, locationCF3, ref_alleleCF4, alt_alleleCF4])
    """
    snps = {}
    for line in file:
        line = split_and_strip(line)
        location = line[3] + '_' + line[4]
        snps[location] = [line[0], line[1], line[2], line[5], line[6]]
    return snps


def update_snp(line, snp_info, count_flip, count_tri_allelic, count_snp_id_not_found):
    """
    :param line: input row of pvar file
    :param snp_info: dictionary with CF3 locations and forward alleles for each SNP
    :param count_flip: number count for flipped strands
    :param count_tri_allelic: number count for triallelic SNPs
    :param count_snp_id_not_found: number count for snps for which no SNPid was available
    :return:
    """
    if line[0].startswith('chr'):
        line[0] = re.sub("chr", '', line[0])

    if line[0] == '39' or line[0] == '41': # rename chrom 39 and 41 to X
        line[0] = 'X'
    location = line[0] + '_' + line[1]
    if location in snp_info:
        alleles = [snp_info[location][3], snp_info[location][4]]
        if line[3] in alleles and line[4] in alleles: # check if alleles are in snp_info dictionary
            # update SNP id
            line[2] = snp_info[location][0]
        # if alleles in pvar file are not the same as forward alleles, flip strand
        elif line[3] not in alleles or line[4] not in alleles:
            flip = str.maketrans("ATCG", "TAGC")
            line[3] = line[3].translate(flip)
            line[4] = line[4].translate(flip)
            # check if alleles are now correct after flipping strand
            if line[3] in alleles and line[4] in alleles:
                count_flip += 1
                # update SNP id
                line[2] = snp_info[location][0]
            # if alleles are still not the same as correct forward alleles, change SNP id to '.'
            elif line[3] not in alleles or line[4] not in alleles:
                count_tri_allelic += 1


        if line[2] != '.': # if snp has a SNPid
            # change location CF3 to CF4
            line[0] = snp_info[location][1] # chromosome update
            line[1] = snp_info[location][2] # bp location update
            # divide chr 39 over 39 and 41 (pseudo-autosomal)
            if line[0] == '39' or line[0] == '41' or line[0] == 'X':
                if int(line[1]) < 6640000:
                    line[0] = '41'
                else:
                    line[0] = '39'
            elif line[0] == 'Y':
                line[0] = '40'
            elif line[0] == 'MT':
                line[0] = '42'

            # update INDEL snps, A=insertion, G=deletion
            if line[2].endswith('_INDEL'):  # line[2] is SNP id
                if len(line[3]) > len(line[4]):
                    line[3] = 'A'  # insertion
                    line[4] = 'G'  # deletion
                else:
                    line[3] = 'G'  # deletion
                    line[4] = 'A'  # insertion
            # if snp was found, delete this snp from dictionary, so no duplicate SNPs end up in pvar file
            # (second snp of duplicate gets '.' for snp id).
            del snp_info[location]

    else:
        count_snp_id_not_found += 1
    return line, snp_info, count_flip, count_tri_allelic, count_snp_id_not_found


def get_snps_to_extract(line, count_kept, count_removed, writer_extract):
    """
    :param line: input row of pvar file
    :param count_kept: number count of extracted SNPs
    :param count_removed: number count of SNPs that will not be extracted, and thus removed
    :param writer_extract: writer for new file with snps to extract
    :return: updated list with SNPs to extract, number count of SNPs to extract and to remove
    """
    if line[2] != '.':  # line[2] is SNP id
        writer_extract.writerow([line[2]])
        count_kept += 1
    elif line[2] == '.':
        count_removed += 1
    return count_kept, count_removed


def main():
    """"
    Creates a new pvar file and a SNPSToExtract list file to use in plink --extract
    """

    # input files
    filename_pvar = sys.argv[1]  # input plink .pvar file
    filename_cf34 = "convert_files/VCF4/SNPs_CF3_CF4.txt"  # file with locations in canfam 3 and canfam 4 for liftover and forward alleles in CF4

    # output files
    newfile_pvar = sys.argv[2] + '.pvar'
    snps_to_extract = sys.argv[2] + '_extract.list'

    with open(filename_pvar, mode="r") as DataPVAR, \
            open(filename_cf34, mode="r") as DataCF34, \
            open(newfile_pvar, "w", newline='') as NewFilePVAR, \
            open(snps_to_extract, "w", newline='') as NewFileExtractedSNPs:
        writer_extract = csv.writer(NewFileExtractedSNPs, delimiter='\t')
        writer_pvar = csv.writer(NewFilePVAR, delimiter='\t')

        count_flip, count_tri_allelic, count_removed, count_kept, count_snp_id_not_found = 0, 0, 0, 0, 0

        snp_info = get_snp_info(DataCF34)

        writer_pvar.writerow(['#CHROM', 'POS', 'ID', 'REF', 'ALT'])
        for line in DataPVAR:
            if line.startswith('#'):
                continue
            line = split_and_strip(line)
            line[2] = '.' # for all snps, make id '.'
            # update location, and snp_id
            line, snp_info, count_flip, count_tri_allelic, count_snp_id_not_found = update_snp(line, snp_info, count_flip, count_tri_allelic, count_snp_id_not_found)
            count_kept, count_removed = get_snps_to_extract(line, count_kept, count_removed, writer_extract)
            writer_pvar.writerow(line)

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