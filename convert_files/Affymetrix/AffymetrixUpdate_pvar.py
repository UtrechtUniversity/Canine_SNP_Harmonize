"""
This script:
Updates .pvar plink file
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
        snp = line[2]
        alleles[snp] = [line[4], line[5]]

    return alleles

def update_alleles(line, alleles):
    """
    :param line: row of input pvar file
    :param alleles: dictionary with snp ID and their alleles
    :return: row with alleles, . is replaced by allele
    """
    if line[2] in alleles.keys():  # line[1] is SNP id
        # if allele = . (not known, because it is missing in all animals), update this allele to the known allele for this SNP
        if line[3] == '.' and line[4] == '.':
            line[3] = alleles[line[2]][0]
            line[4] = alleles[line[2]][1]
        elif line[3] == '.':
            if line[4] == alleles[line[2]][0]:
                line[3] = alleles[line[2]][1]
            elif line[4] == alleles[line[2]][1]:
                line[3] = alleles[line[2]][0]
        elif line[4] == '.':
            if line[3] == alleles[line[2]][0]:
                line[4] = alleles[line[2]][1]
            elif line[3] == alleles[line[2]][1]:
                line[4] = alleles[line[2]][0]
    return line


def main():
    # input files
    filename_pvar = sys.argv[1]
    filename_alleles = 'convert_files/Affymetrix/Affy_forward.txt'

    # output files
    filename_new_pvar = sys.argv[2]

    with open(filename_pvar, mode="r") as DataPvar, \
            open(filename_alleles, mode="r") as DataAlleles, \
            open(filename_new_pvar, "w", newline='') as NewFilePvar:

        writer_pvar = csv.writer(NewFilePvar, delimiter='\t')

        alleles = get_alleles(DataAlleles)

        # write header for pvar file
        writer_pvar.writerow(['##chrSet=<ID=1,autosomePairCt=38,X,Y,XY,M,PAR1,PAR2>'])
        writer_pvar.writerow(['#CHROM', 'POS', 'ID', 'REF', 'ALT'])
        for line in DataPvar:
            if line.startswith('#'):
                continue
            line = split_and_strip(line)
            line = update_alleles(line, alleles)
            writer_pvar.writerow(line)

main()


