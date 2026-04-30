"""
This script:
Updates .pvar plink file
    adds missing alleles (replaces . by an allele)
    flips alleles that are not in forward
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
    :param file: input file with forward alleles for each SNP
    :return: dictionary with alleles per SNP
    """
    alleles = {}
    for line in file:
        line = split_and_strip(line)
        snp = line[0]
        alleles[snp] = [line[1], line[2]]

    return alleles

def check_and_update_alleles(line, alleles, count_not_forward):
    """
    :param line: row of input pvar file
    :param alleles: dictionary with snp ID and their alleles
    :param count_not_forward: how many alleles are not notated in forward and have to be flipped
    :return: row with alleles, . is replaced by allele
    """
    if line[2] in alleles.keys():  # line[2] is SNP id
        # if allele = . (not known, because it is missing in all animals), update this allele to the known allele for this SNP
        if line[3] == '.' and line[4] == '.':
            line[3] = alleles[line[2]][0]
            line[4] = alleles[line[2]][1]

        elif line[3] == '.': # if only 1 allele is known, add the other allele
            if line[4] in alleles[line[2]]:
                if line[4] == alleles[line[2]][0]:
                    line[3] = alleles[line[2]][1]
                elif line[4] == alleles[line[2]][1]:
                    line[3] = alleles[line[2]][0]
            else: # in case the allele is not in the known forward alleles, flip allele
                count_not_forward += 1
                if line[4] == 'A':
                    line[4] = 'T'
                elif line[4] == 'T':
                    line[4] = 'A'
                elif line[4] == 'G':
                    line[4] = 'C'
                elif line[4] == 'C':
                    line[4] = 'G'
                if line[4] == alleles[line[2]][0]:
                    line[3] = alleles[line[2]][1]
                elif line[4] == alleles[line[2]][1]:
                    line[3] = alleles[line[2]][0]
        elif line[4] == '.': # if only 1 allele is known, add the other allele
            if line[3] in alleles[line[2]]:
                if line[3] == alleles[line[2]][0]:
                    line[4] = alleles[line[2]][1]
                elif line[3] == alleles[line[2]][1]:
                    line[4] = alleles[line[2]][0]
            else: # in case the allele is not in the known forward alleles, flip allele
                count_not_forward += 1
                if line[3] == 'A':
                    line[3] = 'T'
                elif line[3] == 'T':
                    line[3] = 'A'
                elif line[3] == 'G':
                    line[3] = 'C'
                elif line[3] == 'C':
                    line[3] = 'G'
                if line[3] == alleles[line[2]][0]:
                    line[4] = alleles[line[2]][1]
                elif line[3] == alleles[line[2]][1]:
                    line[4] = alleles[line[2]][0]
        elif line[3] not in alleles[line[2]] and line[4] not in alleles[line[2]]: # flip alleles because they are not in forward
            count_not_forward += 1
            if line[3] == 'A':
                line[3] = 'T'
            elif line[3] == 'T':
                line[3] = 'A'
            elif line[3] == 'G':
                line[3] = 'C'
            elif line[3] == 'C':
                line[3] = 'G'
            if line[4] == 'A':
                line[4] = 'T'
            elif line[4] == 'T':
                line[4] = 'A'
            elif line[4] == 'G':
                line[4] = 'C'
            elif line[4] == 'C':
                line[4] = 'G'
    return line, count_not_forward


def main():
    # input files
    filename_pvar = sys.argv[1]
    filename_alleles = 'convert_files/wisdom/WisdomForwardAlleles.txt'

    # output files
    filename_new_bim = sys.argv[2]

    with open(filename_pvar, mode="r") as DataPvar, \
            open(filename_alleles, mode="r") as DataAlleles, \
            open(filename_new_bim, "w", newline='') as NewFilePvar:

        writer_pvar = csv.writer(NewFilePvar, delimiter='\t')

        alleles = get_alleles(DataAlleles)

        # write header for .pvar file
        writer_pvar.writerow(["##chrSet=<ID=1,autosomePairCt=38,X,Y,XY,M,PAR1,PAR2>"])

        count_not_forward = 0

        for line in DataPvar:
            if line.startswith('##'):
                continue
            line = split_and_strip(line)
            line, count_not_forward = check_and_update_alleles(line, alleles, count_not_forward)
            writer_pvar.writerow(line)

        print("Number of SNPs of which alleles were not in forward calling, which were updated to forward calling: ", count_not_forward)
main()


