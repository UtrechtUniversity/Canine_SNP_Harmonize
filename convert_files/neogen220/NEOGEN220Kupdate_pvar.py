"""
This script:
Compares callrate between duplicate SNPs
Adds SNP with lowest callrate to file with SNPs to exclude
Updates .pvar plink file
    adds missing alleles (replaces . by an allele)
"""
import csv
import sys
import re


def split_and_strip(line, delimiter="\t"):
    """
    :param line: row of input file
    :param delimiter: which delimiter to use
    :return: stripped and split row
    """
    split_line = line.strip().split(delimiter)
    return split_line

def compare_snp_callrate(file):
    """
    :param file: input file plinks .vmiss
    :return: set op duplicate SNP ids to be excluded
    """
    all_snps = {}
    dup_snps_remove = set()
    for line in file:
        line = split_and_strip(line)
        snp = line[0] + '_' + line[1]
        snp_name = line[2]
        if snp not in all_snps:
            all_snps[snp] = [snp_name, line[3]]
        elif snp in all_snps and snp_name not in dup_snps_remove: # check if snp is duplicate (already present in all_snps dict.)
            if int(line[3]) <= int(all_snps[snp][1]): # compare missingness between duplicate snps
                dup_snps_remove.add(all_snps[snp][0]) # add snp with highest missingness to set with dup snps to remove
            else:
                dup_snps_remove.add(snp_name)
    return dup_snps_remove

def update_excluded_snps(dup_snps_remove, writer):
    """
    :param dup_snps_remove: set of duplicate SNPs to be excluded
    :param writer: writer to update file containing SNPs to exclude
    """
    for snp in dup_snps_remove:
        writer.writerow([snp])

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

def update_ids(line, dup_snps_remove):
    """
    :param line: input row of pvar file
    :param dup_snps_remove: set of duplicate SNPs to be excluded
    :return: updated row of pvar file
    """
    if line[2] not in dup_snps_remove:
        line[2] = re.sub("(_DUP.*)", "", line[2]) # remove _DUP extension for duplicate SNPs that are not removed
    return line

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
    filename_vmiss = sys.argv[1] # file generated with --missing by plink2
    filename_pvar = sys.argv[2]
    filename_alleles = 'convert_files/neogen220/Neogen220KTOPAlleles.txt'

    # output files
    filename_new_pvar = sys.argv[3]
    neogen_snps_to_exclude = sys.argv[4]  # File with SNPids to use in --exclude plink

    with open(filename_vmiss, mode="r") as DataMissing, \
            open(filename_pvar, mode="r") as DataPvar, \
            open(filename_alleles, mode="r") as DataAlleles, \
            open(filename_new_pvar, "w", newline='') as NewFilePvar, \
            open(neogen_snps_to_exclude, "a", newline='') as FileExcludedSNPs:

        writer_exclude = csv.writer(FileExcludedSNPs, delimiter='\t')
        writer_pvar = csv.writer(NewFilePvar, delimiter='\t')

        dup_snps_remove = compare_snp_callrate(DataMissing) # compare callrate between duplicate SNPs
        update_excluded_snps(dup_snps_remove, writer_exclude)

        alleles = get_alleles(DataAlleles)

        # write header for pvar file
        writer_pvar.writerow(['##chrSet=<ID=1,autosomePairCt=38,X,Y,XY,M,PAR1,PAR2>'])
        writer_pvar.writerow(['#CHROM', 'POS', 'ID', 'REF', 'ALT'])
        for line in DataPvar:
            if line.startswith('#'):
                continue
            line = split_and_strip(line)
            line = update_ids(line, dup_snps_remove)
            line = update_alleles(line, alleles)
            writer_pvar.writerow(line)

main()


