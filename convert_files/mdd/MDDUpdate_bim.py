"""
This script:
Updates .bim plink file
    adds missing alleles (replaces . by an allele)
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

def update_alleles(line, alleles):
    """
    :param line: row of input bim file
    :param alleles: dictionary with snp ID and their alleles
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
    return line


def main():
    # input files
    filename_bim = sys.argv[1]
    filename_alleles = 'convert_files/mdd/MDDTOPAlleles.txt'

    # output files
    filename_new_bim = sys.argv[2]

    with open(filename_bim, mode="r") as DataBim, \
            open(filename_alleles, mode="r") as DataAlleles, \
            open(filename_new_bim, "w", newline='') as NewFileBim:

        writer_bim = csv.writer(NewFileBim, delimiter='\t')

        alleles = get_alleles(DataAlleles)

        for line in DataBim:
            line = split_and_strip(line)
            line = update_alleles(line, alleles)
            writer_bim.writerow(line)

main()


