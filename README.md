<p align="center">
    <a href="https://www.uu.nl/en/research/expertise-centre-for-veterinary-genetics" target="_blank">
        <img src="convert_files/common_files/Logo.png" alt="Utrecht University Logo">
    </a>
</p>

<h1 align="center">Pipeline for harmonizing canine SNP data</h1>

-----------------------------------------------------------------------------
This project is part of the [Expertise Centre for Veterinary Genetics](https://www.uu.nl/en/research/expertise-centre-for-veterinary-genetics), Faculty of Veterinary Medicine, Utrecht University

Our github team repositories: [ECG](https://github.com/orgs/UtrechtUniversity/teams/expertise-centre-for-veterinary-genetics/repositories)

## Project description:
To be able to merge genotype files from different platforms, the files must be in a uniform format. 
This genotype processing pipeline (command line tool) creates files which are in the same format, 
ready to be merged.

This command line utility can be used for the following platforms:
- Embark 80K-230K
- VHL Genetics 33K
- Neogen 170K array (Illumina CanineHD BeadChip)
- Neogen 220K array (Illumina CanineHD BeadChip)
- Lupa 170K array
- MyDogDNA (mdd) 15K
- Wisdom 15K
- WGS canfam 3 (vcf file)
- WGS canfam 4 (vcf file)
- Affymetrix/Axiom


### Command line utility convert.sh
Input files should be in same folder as convert.sh script. In this folder should also be the convert_files folder.

Usage: bash convert.sh [-i|e|a|o|f|n|w|v|t|l|p|h]
Command line tool to convert input files to a uniform format
- Syntax options:
  - -i <filename.bim>       Specify full name of .bim file 
  - -e <filename.bed>       Specify full name of .bed file 
  - -a <filename.fam>       Specify full name of .fam file 
  - -o <prefix_filename>    Specify prefix for output files. Obligatory 
  - -f <prefix_filename>    Specify prefix for .bed + .fam +. bim file 
  - -n <filename>           Specify full name of final report file of Neogen 220K or 170K 
  - -w <filename>           Specify full name of Wisdom file (xlsx)
  - -v <filename>           Specify full name of VCF.gz canfam 3 or 4 file (WGS)
  - -t                      To indicate a .tbi file of the VCF file is already present, and skip the step of indexing the raw vcf
  - -l                      To indicate a file with filtered locations from raw vcf file is present, and skip step of filtering locations
  - -p <platform>           Specify platform, options: embark, vhl, neogen170, neogen220, lupa170, mdd, wisdom, affymetrix, vcf3, vcf4. Obligatory 
  - -h                      Print the help overview

- Examples:
  - bash convert.sh -f inputfile -p embark -o newfilename 
  - bash convert.sh -a inputfile.fam -i inputfile.bim -e inputfile.bed -p mdd -o newfilename
  - bash convert.sh -n inputfile -p neogen220 -o newfilename
  - bash convert.sh -v inputfile.vcf.gz -t -p vcf3 -o newfilename
  - bash convert.sh -v inputfile_filtered_locations.vcf -l -p vcf3 -o newfilename
- Dependencies needed:
  - python3, with packages pandas and openpyxl (only needed for converting wisdom files)
  - perl
  - plink2

Syntax options per platform:
- -p embark:
  - For specifying input files, use either -i,-e-,a together, or only -f. 
  - Options -n, -w, -v, -t, -l cannot be used 
  - For platform use -p embark
- -p vhl:
  - For specifying input files, use either -i,-e-,a together, or only -f. 
  - Options -n, -w, -v, -t, -l cannot be used 
  - For platform use -p vhl
- -p neogen220:
  - For specifying input files, use -n 
  - Options -i,-e-,a,-f, -w, -v, -t, -l cannot be used 
  - For platform use -p neogen220
- -p neogen170:
  - For specifying input files, use -n 
  - Options -i,-e-,a,-f, -w, -v, -t, -l cannot be used 
  - For platform use -p neogen170 
- -p wisdom:
  - For specifying input files, use -w 
  - Options -i,-e-,a,-f, -n, -v, -t, -l cannot be used 
  - For platform use -p wisdom 
- -p mdd:
  - For specifying input files, use either -i,-e-,a together, or only -f. 
  - Options -n, -w, -v, -t, -l cannot be used 
  - For platform use -p mdd 
- -p lupa170:
  - For specifying input files, use either -i,-e-,a together, or only -f. 
  - Options -n, -w, -v, -t, -l cannot be used 
  - For platform use -p lupa170
- -p vcf3:
  - For specifying input files, use -v 
  - Use -t to indicate .tbi (indexed vcf) file is already present. Use in combination with -v. 
  - Use -l to indicate .vcf file with filtered locations from the raw vcf file is already present. Specify file with -v.
  - Options -i,-e-,a,-f, -n, -w cannot be used 
  - For platform use -p vcf3
- -p vcf4:"
  - For specifying input files, use -v 
  - Use -t to indicate .tbi (indexed vcf) file is already present. Use in combination with -v. 
  - Use -l to indicate .vcf file with filtered locations from the raw vcf file is already present. Specify file with -v.
  - Options -i,-e-,a,-f, -n, -w cannot be used 
  - For platform use -p vcf4
- -p affymetrix
  - For specifying input files, use either -i,-e-,a together, or only -f.
  - Options -n, -w, -v, -t, -l cannot be used
  - For platform use -p affymetrix

## Operating system: Linux
This command line utility operates in Linux and is tested in Ubuntu, so it is advised to use Ubuntu. If you have a Windows system,
a Windows Subsystem for Linux (WSL) should be used. Installation information can be found on the ubuntu website.

## Operating system and used program versions
- convert.sh 
  - This command line utility operates in Linux and is tested in Ubuntu, so it is advised to use Ubuntu. If you have a Windows system,
  a Windows Subsystem for Linux (WSL) should be used. Installation information can be found on the ubuntu website.
- Used versions to test the tools:
  - Ubuntu 24.04.3 LTS noble
  - Perl 5, version 38, subversion 2 (v5.38.2) built for x86_64-linux-gnu-thread-multi
  - Python 3.12.3
    - pandas 2.1.4
    - openpyxl 3.1.2
  - Plink 2, tested with version PLINK v2.0.0-a.6.32LM AVX2 Intel (10 Jan 2026)

### SNP information
- How alleles are called can differ. They can be coded in Forward/dbsnp, TOP, A/B and 1/2. 
To merge files, all files must be in the same allele coding.
- The dog has 38 autosomal chromosomes. The additional SNPs are placed on a 'chromosome' as followed: 
On 39 are the non-pseudo-autosomal X chromosome SNPs, on 40 are the Y-chromosome SNPs, on 41 are the
pseudo-autosomal X-chromosome SNPs and on 42 are the mitochondrial SNPs.

### File descriptions (common files folder):
- SNPsToExcludeMerge.list
  - This file contains SNPs that have to be excluded when merging files from different platforms
  - SNPs on this list have locations that do not match between files 
  (for example, SNP123 has different location in Embark, compared to Illumina)
  - These SNPs are added to each platforms ExcludedSNPs file, on which are also SNPs that have to be removed for this
  platform specifically.
- SNP_Table_Big.txt
  - snp table used in perl script to change allele calling. All SNPs are in ATCG format, also the indel SNPs
- SNP_Table_Big_Forward.bim
  - SNPs from the SNP_Table_Big.txt in their forward calling, is used for checking correct allele calls
  in WGS files

### Plink settings
- --chr-set 38 is used in command (not --dog)
  - By doing this, the chromosome coding will remain the same (all in numbers from 1 to 42). 
  - Dog has 38 autosomes
- --output-chr 26 to make sure chromosome IDs are always numeric (and not X, Y, MT)

For each platform, the actions performed by the command line utility are explained below.

## Embark
**Summary raw data:**
- SNP array of 229991 or 82434 SNPs
- Type of allele calling: TOP
- Contains data of X (chr 39), X-pseudo autosomal (chr 41), Y (chr 40) and mitochondrial (chr 42) SNPs
- Contains SNPids that are different in other platform arrays for the same SNP
- Contains SNPs that seem to call a wrong allele (other platforms call other allele, and allele not found in Ensemble, EBI-EVA)
- Contains SNPs that seem to have a wrong location (sometimes old canfam2 location)
- Contains SNPs without a location
- Contains indels
- Contains duplicate SNPs
- Not all SNPs are written completely in uppercase and some SNPs have _rs numbers in SNP id
- CanFam 3.1

**Embark files**
- EmbarkSNPIdConversion
  - File with the SNP id's that have multiple names between arrays, contains the embark ID and the ID used in other platforms
- EmbarkDuplicatesOrWrongAllele
  - File with SNP id's of duplicate snps and if one of the pair calls the wrong alleles
- EmbarkCorrectSNPPositions.map
  - File with SNPs of which correct locations and chromosomes are known.
    - locations that did not match with other arrays were checked in ensembl or by doing liftover if canfam 2 or 4 locations were available
- EmbarkCorrectAlleles.bim
  - File with SNPs that call wrong alleles in raw data files, with their correct alleles
  - Alleles were compared to other platform arrays and Ensemble, EBI-EVA
- EmbarkIndelSNPs.txt
  - file with SNPs that are coding for indels

**Steps performed by the command line utility for getting the right format for Embark:**
1. Make .vmiss plink file with --missing to get missingness per SNP (to use for deciding which duplicate snp to remove)
2. EMBARKconvertBIM.py script
   - Creates a new file with a list of SNP id's to be excluded using --exclude in plink
     - SNPs on chromosome 0 or bp position 0 (= no location available) or with a wrong location that could not be corrected
     - SNPs that are in the list 'SNPsToExcludeMerge'
     - SNPs that are duplicate
   - Creates a new BIM file with these changes:
     - Removes _ilmndup and _rsnumber from SNP id
     - Makes SNP id's uppercase
     - adds _INDEL to SNP id (for insertion/deletion SNPs)
     - for SNPs without or wrong location, location and chromosome is updated using EmbarkCorrectSNPPositions.map
     - changes wrong alleles to correct alleles using EmbarkCorrectAlleles.bim
     - Change SNP id if SNP also has different ID in other arrays (some SNPs in embark are the same as for example in 
     Neogen and have the same location, but have a different SNP id)
3. Order the SNPs on chromosome+location with plink --sort-vars to prevent errors in plink2
4. The generated ExcludedSNPs list is used in plink --exclude to remove SNPs


## VHL
**Summary raw data:**
- SNP array of 33928 SNPs
- Type of allele calling: TOP
- Contains data of X (chr 39), X-pseudo autosomal (chr 41), mitochondrial (chr 42), but no Y SNPs
  - SNPs on X (39) chromosome are not yet divided over 'chromosome' 39 and 41
- Contains SNPs that have a different SNPid in other arrays
  - VHL has SNP ids that only consist of numbers
- Contains duplicate SNPs
- Contains SNPs without a location
- Contains indels but only for SNPs without a location. So these are all filtered out.
- CanFam 3.1

**VHL files**
- VHL_snp_info.txt
  - File with per SNP, the location, the SNPid in VHL, SNPid as in other arrays, and the known correct alleles
  - For a few VHL SNPs, no correct alleles are known, and are not in this file

**Steps performed by the command line utility for getting the right format for VHL:**
1. Make .vmiss plink file with --missing to get missingness per SNP (to use for deciding which duplicate snp to remove)
2. VHLconvert.py script
   - Creates a new file with a list of SNP id's to be excluded using --exclude in plink
     - SNPs on chromosome 0 or bp position 0 (= no location available)
     - SNPs that are in the list 'SNPsToExcludeMerge'
     - SNPs with incorrect alleles or alleles that could not be checked
   - Creates a new BIM file with these changes:
     - Change SNP id if SNP also has different ID in other arrays
     - Changes chromosome 39 to 39 or 41 if pseudo-autosomal (if location < 6640000 bp)
   - Creates a new FAM file with these changes:
     - The PLINK FID (family ID) is changed to the same id as the IID (individual ID)
3. Order the SNPs on chromosome+location with plink --sort-vars to prevent errors in plink2
4. The generated ExcludedSNPs list is used in plink --exclude to remove SNPs


## Neogen 170K
**Summary raw data:**
- SNP array of 173661 SNPs
- Type of allele calling: TOP, forward and A/B
- No duplicate SNPs
- Contains data of X and X-pseudo-autosomal, Y, no mitochondrial
  - SNPs on X (39) chromosome are not yet divided over 'chromosome' 39 and 41
- Not all SNPs are written completely in uppercase
- Some SNPs have _rsnumber in ID name
- Canfam 2

**Neogen 170K files:**
- Neogen170KsnpsPresentInCF3.map 
  - map file with snps in canfam 3.1 (locations were lifted from cf2 to cf 3.1). The snps that failed are not in this file.
- Neogen170KsnpsNotPresentInCF3.map 
  - map file with snps that could not be lifted from canfam 2 to canfam 3.1
- Neogen170KCorrectAlleles.bim
  - file with correct alleles for snps that call wrong alleles
- Neogen170KTOPAlleles.txt
  - File with known TOP alleles for each SNP

**Steps performed by the command line utility for getting the right format for neogen 170 K:**
1. NEOGEN170Kconvert.py script
   - Creates a PED file with these changes:
     - For missing alleles, - is changed to 0
     - Corrects wrong alleles
   - Creates a MAP file with these changes:
     - Removes _rsnumber from SNP id 
     - Makes SNP id's uppercase
     - Changes chromosome X to 39 or 41 if pseudo-autosomal (if location < 6640000 bp)
     - Changes chromosome Y to 40
     - Updates location and chromosome to canfam 3.1
   - Creates a new file with a list of SNP id's to be excluded using --exclude in plink
     - SNPs without location
     - SNPs that could not be liftover to canfam 3.1
     - SNPs on the SNPsToExcludeMerge.list
2. Order the SNPs on chromosome+location with plink --sort-vars to prevent errors in plink2
3. Adding missing alleles info to .pvar file, with script NEOGEN170Kupdate_pvar.py
4. The generated ExcludedSNPs list is used in plink --exclude to remove SNPs

## Neogen 220K
**Summary raw data:**
- SNP array of 220853 SNPs
- Type of allele calling: TOP, forward and A/B
- Contains indels
- Contains duplicate SNPs
- Contains SNPids that are different in other platform arrays for the same SNP
- Contains data of X and X-pseudo-autosomal, Y, and mitochondrial
  - SNPs on X (39) chromosome are not yet divided over 'chromosome' 39 and 41
  - Mitochondrial SNPs are on chromosome 'MT'
- Not all SNPs are written completely in uppercase
- Some SNPs have _rsnumber in ID name
- Contains SNPs that seem to call a wrong allele (other platforms call other allele, and allele not found in Ensemble, EBI-EVA)
- Contains SNPs that seem to have a wrong location
- CanFam 3.1

**Neogen 220K files:**
- Neogen220K_Indels.txt
  - Indel snps present in Neogen 220K
- Neogen220K_SNP_Map_CF3.txt
  - Information Neogen provides about the SNPs (locations, alleles etc.)
- Neogen220KTOPAlleles.txt
  - File with known TOP alleles for each SNP
- Neogen220KchrYsnpDifferentLocations.txt
  - File with chr Y SNPs with abnormal locations
- Neogen220KDuplicates.txt
  - File with duplicate snps
- Neogen220KIncorrectAlleles.bim
  - file with incorrect and correct alleles for snps that call wrong alleles
- Neogen220KSNPsIdConversion
  - File with the SNP id's that have multiple names between arrays, contains the neogen ID and the ID used in other platforms
- Neogen220KSNPsMissingLocation
  - file with locations of snps derived from other arrays, to use as location for snps in neogen
  without location.

**Steps performed by the command line utility for getting the right format for Neogen 220K:**
1. NEOGEN220Kconvert.py
   - Creates a PED file with these changes:
     - For missing alleles, - is changed to 0
     - For indel snps, changes the I/D calls to I=A, D=G
     - updates wrong alleles
   - Creates a MAP file with these changes:
     - Removes _rsnumber from SNP id 
     - adds _INDEL to SNP id (for insertion/deletion SNPs)
     - Makes SNP id's uppercase
     - Updates IDs to match the names in other platforms/arrays
     - Changes chromosome X to 39 or 41 if pseudo-autosomal (if location < 6640000 bp)
     - Changes chromosome Y to 40
     - Changes chromosome MT to 42
     - adds _DUP1 or _DUP2 to duplicates
     - for SNPs without or with wrong location, get location on chromosome from SNP id or from Neogen220KSNPsMissingLocation file
   - Creates a new file with a list of SNP id's to be excluded using --exclude in plink
     - SNPs on chromosome 0 or bp position 0 (= no location available)
     - SNPs that are in the list 'SNPsToExcludeMerge'
2. Order the SNPs on chromosome+location with plink --sort-vars to prevent errors in plink2
3. Make .vmiss plink file with --missing to get missingness per SNP (to use for deciding which duplicate snp to remove)
4. Comparing duplicate SNPs call rates and adding missing alleles, with script NEOGEN220Kupdate_pvar.py
   - Add duplicate SNP with worst call rate to list with SNPs to exclude
5. The generated ExcludedSNPs list is used in plink --exclude to remove SNPs



## Lupa 170K
**Summary raw data:**
- SNP array of 174376 SNPs
- Type of allele calling: Forward
- No duplicate SNPs
- Contains data of X and X-pseudo-autosomal SNPs, no Y or mitochondrial
  - SNPs on X (39) chromosome are not yet divided over 'chromosome' 39 and 41
- SNPs are all in uppercase
- No _rsnumber in SNPid
- CanFam 2

**Lupa 170K files:**
- Lupa174KSNPsNotInTop.txt
  - File with SNPs that could not be converted from forward to TOP calling
- Lupa174KSNPsPresentInCF3.map
  - File with SNPs that have a location in CanFam 3.1
- Lupa174SNPsNotPresentInCF3.map.txt
  - File with SNPs that have no location in CanFam 3.1, only have location in CanFam 2
- convert_bim_allele.pl
  - perl script to change allele calling
- SNP_Table_Big.txt
  - needed for the perl script, contains information about the forward or top calling of alleles

**Steps performed by the command line utility for getting the right format for Lupa 170K:**
1. LUPA174Kconvert.py
   - Creates a BIM file with these changes:
     - Changes chromosome X to 39 or 41 if pseudo-autosomal (if location < 6640000 bp)
     - Updates location and chromosome to canfam 3.1
   - Creates a new file with a list of SNP id's to be excluded using --exclude in plink
     - SNPs that could not be liftover to canfam 3.1
     - SNPs that can not be converted to TOP calling
     - SNPs on the SNPsToExcludeMerge.list
2. Order the SNPs on chromosome+location with plink2 --sort-vars to prevent errors in plink2
3. The generated ExcludedSNPs list is used in plink2 --exclude to remove SNPs
4. Adding missing alleles and flip alleles in .bim file, with script LupaUpdate_bim.py
5. Perl script convert_bim_allele.pl to convert forward allele calling to TOP calling
    - uses SNP_Table_Big.txt
    - convert_bim_allele.pl --intype dbsnp --outtype top --outfile new_bim_file input_bim_file SNP_Table_Big.txt


## MyDogDNA (mdd)
**Summary raw data:**
- SNP array of 15654 SNPs
- Type of allele calling: illumina 1/2
- No duplicate SNPs
- Does not contain X or Y data
- Has 702 unknown SNPs (wisdom gives the SNP id 'unknown', because they are secret SNPs,
MDD does not give information about their location)
- Not all SNPs are written completely in uppercase
- Some SNPs have _rsnumber in ID name
- CanFam 3.1

**Files:**
- convert_bim_allele.pl
  - perl script to change allele calling
- SNP_Table_Big.txt
  - needed for the perl script
- MDDTOPAlleles.txt
  - File with known TOP alleles for each SNP

**Steps performed by the command line utility for getting the right format for MyDogDNA:**
1. MDDconvert.py script
    - Creates a new BIM file with these changes:
      - Removes _rsnumber in SNP id
      - Makes SNP id's uppercase
    - Creates a new FAM file with these changes:
      - if family id is 0, change this value to individual id
    - Creates a new list file with SNPs to exclude and use in --exclude plink:
      - Unknown SNPs
      - SNPs that are in the list 'SNPsToExcludeMerge'
2. Order the SNPs on chromosome+location with plink --sort-vars to prevent errors in plink2
3. The generated ExcludedSNPs list is used in plink --exclude to remove SNPs
4. Replacing '.' by '0' in bim file to prevent errors in next step
5. Perl script convert_bim_allele.pl to convert ilumina 1 2 allele calling to TOP calling
    - uses SNP_Table_Big.txt
    - convert_bim_allele.pl --intype ilmn12 --outtype top --outfile new_bim_file input_bim_file SNP_Table_Big.txt
6. Adding missing alleles info to .bim file, with script MDDUpdate_bim.py


## Wisdom
**Summary raw data:**
- SNP array of ~15788 SNPs
- Type of allele calling: 0-1-2 (after conversion it is in forward)
- No duplicate SNPs
- Contains data of X and X-pseudo-autosomal and Y snps, no mitochondrial snps
- Not all SNPs are written completely in uppercase
- Some SNPs have _rsnumber in ID name
- CanFam 3.1

**Wisdom files:**
- WisdomForwardAlleles.txt
  - File with known Forward alleles for each SNP
- WisdomTranslationTable.txt
  - snps and the alleles that correspond to 0 - 1 - 2
- convert_bim_allele.pl
  - perl script to change allele calling
- SNP_Table_Big.txt
  - needed for the perl script
- Wisdom_incorrect_alleles.txt
  - file with SNPs that call incorrect forward alleles in translation table

**Steps performed by the command line utility for getting the right format for Wisdom:**
1. WisdomConvert.py script
   - Creates a new MAP file with these changes:
     - SNP names to uppercase 
     - RS number removed from SNPname 
     - X chromosome divided over chromosome 41 (pseudo-autosomal) and 39
   - Creates a new PED file with these changes:
     - 0-1-2 allele coding of wisdom is converted to ACTG forward
     - missing alleles are changed to 0
   - Creates a new list file with SNPs to exclude and use in --exclude plink:
     - SNPs without location 
     - SNPs not in translation table
     - SNPs with wrong allele in translation table
2. Order the SNPs on chromosome+location with plink --sort-vars to prevent errors in plink2
3. Adding missing alleles info to variants file and flip alleles that are not in forward, with script WisdomUpdate_bim.py
4. The generated ExcludedSNPs list is used in plink --exclude to remove SNPs
5. Perl script convert_bim_allele.pl to convert forward allele calling to TOP calling
    - uses SNP_Table_Big.txt
    - convert_bim_allele.pl --intype dbsnp --outtype top --outfile new_bim_file input_bim_file SNP_Table_Big.txt


## VCF canfam 3
**Summary raw data:**
- Type of allele calling: forward

**Files:**
- Raw VCF file, with .vcf.gz extension or a VCF file with filtered locations from the raw VCF file as input
- Optional a .tbi file (indexed file of the raw VCF file, made by using tabix)
- Filter file
  - To filter the snps with known SNP ids out of the VCF file
  - Has chromosome's coded as for example 1 and chr1, so both formats can be filtered
- SNPs_forward_alleles.txt in common_files directory. File with SNPs, their locations and forward alleles.
- SNP table for perl script to change forward to TOP snp calling

**Steps performed by the command line utility for getting the right format for VCF in canfam 3:**
First 2 steps are skipped if option -l was used and input file is a vcf file with already filtered locations 
(which is normally done at step 2 with tabix).
1. Index raw VCF file using tabix (only if .tbi file does not exist yet)
   - tabix -p vcf filename.vcf.gz
2. Filter vcf file for known SNPs using tabix
   - tabix -h -R VCFFilterFile.txt filename.vcf.gz > newfilename.vcf
3. Make plink format from VCF in plink and sort SNPs on location
4. VCF3convert.py script
   - Creates a new bim file with these changes: 
     - adds SNP id for known snps, based on base pair position 
     - SNPs on chromosome 39 are divided over 39 and 41 (pseudo-autosomal)
     - flippes strands when needed 
     - changes alleles of indel IDs to fictional alleles A (insertion) and G (deletion)
   - Creates a file with SNPs to extract
     - SNPs with a SNP id
     - bi-allelic SNPs
     - SNPs that are SNPs and not indels, except for the known indels
5. The generated VCF3_extract list is used in plink --extract to extract SNPs
6. Perl script convert_bim_allele.pl to convert forward allele calling to TOP calling
    - uses SNP_Table_Big.txt
    - convert_bim_allele.pl --intype dbsnp --outtype top --outfile new_bim_file input_bim_file SNP_Table_Big.txt


## VCF canfam 4
**Summary raw data:**
- Type of allele calling: forward

**Files:**
- Raw VCF file, with .vcf.gz extension or a VCF file with filtered locations from the raw VCF file as input
- Optional a .tbi file (indexed file of the raw VCF file, made by using tabix)
- Filter file
  - To filter the snps with known SNP ids out of the VCF file
  - Has chromosome's coded as for example 1 and chr1, so both formats can be filtered
- File with SNPs with their IDs and locations in CF3 and CF4, and their forward alleles in CF4
- SNP table for perl script to change forward to TOP snp calling

**Steps performed by the command line utility for getting the right format for VCF in canfam 4:**
First 2 steps are skipped if option -l was used and input file is a vcf file with already filtered locations 
(which is normally done at step 2 with tabix).
1. Index raw VCF file using tabix (only if .tbi file does not exist yet)
   - tabix -p vcf filename.vcf.gz
2. Filter vcf file for known SNPs using tabix
   - tabix -h -R VCFFilterFile.txt filename.vcf.gz > newfilename.vcf
3. Make plink format from VCF in plink and sort SNPs on location
4. VCF4convert.py script
   - Creates a new bim file with these changes: 
     - adds SNP id for known snps, based on base pair position 
     - SNPs on chromosome 39 are divided over 39 and 41 (pseudo-autosomal)
     - flippes strands when needed 
     - changes alleles of indel IDs to fictional alleles A (insertion) and G (deletion)
   - Creates a file with SNPs to extract
     - SNPs with a SNP id
     - bi-allelic SNPs
     - SNPs that are SNPs and not indels, except for the known indels
5. The generated VCF4_extract list is used in plink --extract to extract SNPs
6. Perl script convert_bim_allele.pl to convert forward allele calling to TOP calling
    - uses SNP_Table_Big.txt
    - convert_bim_allele.pl --intype dbsnp --outtype top --outfile new_bim_file input_bim_file SNP_Table_Big.txt


## Affymetrix
**Summary raw data:**
- Multiple SNP arrays
- Type of allele calling: forward
- Contains data (depending on array) of X (chr 39), X-pseudo autosomal (chr 41, in raw array still 39) and  mitochondrial (chr 42) and Y SNPs
- CanFam 3.1

**Files:**
- Affy_forward.txt
  - File with SNP alleles in forward and SNP ids that are on other platforms for the same SNPs
  - To check if SNPs need te be flipped or are wrong, or are tri-allelic
  - To update locations of SNPs that are missing or wrong
  - this file is based on forward alleles in build canfam 3.
- SNP table for perl script

**Steps performed by the command line utility for getting the right format for affymetrix:**
1. AffymetrixConvert.py script
   - Creates a new bim file with these changes: 
     - adds SNP id for known snps ids present on other platforms, based on base pair position 
     - SNPs on chromosome 39 are divided over 39 and 41 (pseudo-autosomal)
     - flips strands when needed
     - changes alleles of indel IDs to fictional alleles A (insertion) and G (deletion)
     - updated locations of SNPs with missing or wrong location
   - Creates a file with SNPs to extract
     - SNPs with a SNP id
     - bi-allelic SNPs
     - SNPs that are SNPs and not indels, except for the known indels
2. Order the SNPs on chromosome+location with plink --sort-vars to prevent errors in plink2
3. Adding missing alleles info to variants file, with script AffymetrixUpdate_pvar.py
4. The generated Affymetrix_extract list is used in plink --extract to extract SNPs
5. Perl script convert_bim_allele.pl to convert forward allele calling to TOP calling
    - uses SNP_Table_Big.txt
    - convert_bim_allele.pl --intype dbsnp --outtype top --outfile new_bim_file input_bim_file SNP_Table_Big.txt

## Credits
This project is part of the [Expertise Centre for Veterinary Genetics](https://www.uu.nl/en/research/expertise-centre-for-veterinary-genetics), Faculty of Veterinary Medicine, Utrecht University
