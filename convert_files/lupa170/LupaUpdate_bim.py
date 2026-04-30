"""
This script:
Updates .bim plink file
    adds missing alleles (replaces . by an allele)
    flips alleles
"""
import csv
import sys


def split_and_strip(line, delimiter="\t"):
    """
    :param line: row of input file
    :param delimiter: which delimiter to use
    :return: stripped and split row
    """
    split_line = line.strip().split(delimiter)
    return split_line


def get_alleles(file):
    """
    :param file: input file with alleles for each SNP
    :return: dictionary with alleles per SNP
    """
    alleles = {}
    for line in file:
        line = split_and_strip(line)
        snp = line[0]
        alleles[snp] = [line[1], line[2]]

    return alleles

def update_alleles(line, alleles, count_flip):
    """
    :param line: row of input bim file
    :param alleles: dictionary with snp ID and their alleles
    :param count_flip: count of SNPs flipped
    :return: row with alleles, . is replaced by allele
    """
    if line[1] in alleles.keys():  # line[1] is SNP id
        # if allele = . (not known, because it is missing in all animals), update this allele to the known allele for this SNP
        if line[4] == '.' and line[5] == '.':
            line[4] = alleles[line[1]][0]
            line[5] = alleles[line[1]][1]
        elif line[4] == '.':
            if line[5] == alleles[line[1]][0]:
                line[4] = alleles[line[1]][1]
            elif line[5] == alleles[line[1]][1]:
                line[4] = alleles[line[1]][0]
        elif line[5] == '.':
            if line[4] == alleles[line[1]][0]:
                line[5] = alleles[line[1]][1]
            elif line[4] == alleles[line[1]][1]:
                line[5] = alleles[line[1]][0]
        elif line[4] not in alleles[line[1]] and line[5] not in alleles[line[1]]: # flip alleles because they are not in forward
            count_flip += 1
            if line[4] == 'A':
                line[4] = 'T'
            elif line[4] == 'T':
                line[4] = 'A'
            elif line[4] == 'G':
                line[4] = 'C'
            elif line[4] == 'C':
                line[4] = 'G'
            if line[5] == 'A':
                line[5] = 'T'
            elif line[5] == 'T':
                line[5] = 'A'
            elif line[5] == 'G':
                line[5] = 'C'
            elif line[5] == 'C':
                line[5] = 'G'
    return line, count_flip


def main():
    # input files
    filename_bim = sys.argv[1]
    filename_alleles = 'convert_files/lupa170/LupaForwardAlleles.txt'

    # output files
    filename_new_bim = sys.argv[2]

    with open(filename_bim, mode="r") as DataBim, \
            open(filename_alleles, mode="r") as DataAlleles, \
            open(filename_new_bim, "w", newline='') as NewFileBim:

        writer_bim = csv.writer(NewFileBim, delimiter='\t')

        alleles = get_alleles(DataAlleles)
        count_flip = 0
        for line in DataBim:
            line = split_and_strip(line)
            line, count_flip = update_alleles(line, alleles, count_flip)
            writer_bim.writerow(line)

        print("Number of SNPs of which alleles were flipped: ", count_flip)

main()


