# ATaRVa - a tandem repeat genotyper
![Badge-PyPI](https://img.shields.io/badge/PyPI-v0.3.0-brightgreen)
![Badge-License](https://img.shields.io/badge/License-MIT-blue)

<p align=center>
  <img src="lib/atrv_logo.png" alt="Logo of ATaRVa" width="200"/>
</p>

ATaRVa (pronounced uh-thur-va, IPA: /əθərvə/, Sanskrit: अथर्व) is a technology-agnostic tandem repeat genotyper, specially designed for long read data. The name expands to **A**nalysis of **Ta**ndem **R**epeat **Va**riation, and is derived from the the Sanskrit word _Atharva_ meaning knowledge.


## Motivation
Long-read sequencing propelled comprehensive analysis of tandem repeats (TRs) in genomes. Current long-read TR genotypers are either platform specific or computationally inefficient. ATaRva outperforms existing tools while running an order of magnitude faster. ATaRVa also supports short-read data, multi-threading, haplotyping, and motif decomposition, making it an invaluable tool for population scale TR analyses.   

## Installation

ATaRVa can be directly installed using pip with the package name `ATaRVa`.

```bash
$ pip install ATaRVa
```
Alternatively, it can be installed from the source code:<br>
It is recommended to install this inside a Python virtual environment.

```bash
# Create a python env
$ python -m venv atarva_env

# Activate the env
$ source atarva_env/bin/activate
$ pip install build

# Download the git repo
$ git clone https://github.com/SowpatiLab/ATaRVa.git

# Install
$ cd ATaRVa
$ python -m build
$ pip install .

# Deactivate the env
$ deactivate
```
Both of the methods add a console command `atarva`, which can be executed from any directory

<!-- **NOTE: This tool has been tested and is recommended to be used with Python versions between 3.9 and 3.12 (inclusive).** -->

### Docker installation
ATaRVa can also be installed using the provided **Docker** image with the following steps:
```bash
$ cd ATaRVa
$ docker build --network host -t atarva
```

## Usage
The help message and available options can be accessed using

```bash
$ atarva -h
#  or
$ atarva --help
```
which gives the following output

```
usage: atarva [-h] -f <FILE> -b <FILE> [<FILE> ...] -r <FILE> [--format <STR>] [-q <INT>]
              [--contigs CONTIGS [CONTIGS ...]] [--min-reads <INT>] [--max-reads <INT>]
              [--snp-dist <INT>] [--snp-count <INT>] [--snp-qual <INT>] [--flank <INT>]
              [--snp-read <FLOAT>] [--phasing-read <FLOAT>] [-o <FILE>]
              [--karyotype KARYOTYPE [KARYOTYPE ...]] [-t <INT>] [--haplotag <STR>]
              [--decompose] [--amplicon] [-log] [-v]

Required arguments:
  -f <FILE>, --fasta <FILE>
                        input reference fasta file
  -b <FILE> [<FILE> ...], --bam <FILE> [<FILE> ...]
                        samples alignment files. allowed formats: SAM, BAM, CRAM
  -r <FILE>, --regions <FILE>
                        input regions file. the regions file should be strictly in bgzipped
                        tabix format. If the regions input file is in bed format. First sort it
                        using bedtools. Compress it using bgzip. Index the bgzipped file with
                        tabix command from samtools package.

Optional arguments:
  --format <STR>        format of input alignment file. allowed options: [cram, bam, sam]. default: [bam]
  -q <INT>, --map-qual <INT>
                        minimum mapping quality of the reads to be considered. [default: 5]
  --contigs CONTIGS [CONTIGS ...]
                        contigs to get genotyped [chr1 chr12 chr22 ..]. If not mentioned every
                        contigs in the region file will be genotyped.
  --min-reads <INT>     minimum read coverage after quality cutoff at a locus to be genotyped. [default: 10]
  --max-reads <INT>     maximum number of reads to be used for genotyping a locus. [default: 100]
  --snp-dist <INT>      maximum distance of the SNP from repeat region to be considered for
                        phasing. [default: 3000]
  --snp-count <INT>     number of SNPs to be considered for phasing (minimum value = 1).
                        [default: 3]
  --snp-qual <INT>      minimum basecall quality at the SNP position to be considered for
                        phasing. [default: 13]
  --flank <INT>         length of the flanking region (in base pairs) to search for insertion
                        with a repeat in it. [default: 10]
  --snp-read <FLOAT>    a positive float as the minimum fraction of snp's read contribution to
                        be used for phasing. [default: 0.25]
  --phasing-read <FLOAT>
                        a positive float as the minimum fraction of total read contribution from
                        the phased read clusters. [default: 0.4]
  -o <FILE>, --vcf <FILE>
                        name of the output file, output is in vcf format. [default: sys.stdout]
  --karyotype KARYOTYPE [KARYOTYPE ...]
                        karyotype of the samples [XY XX]
  -t <INT>, --threads <INT>
                        number of threads. [default: 1]
  --haplotag <STR>      use haplotagged information for phasing. eg: [HP]. [default: None]
  --decompose           write the motif-decomposed sequence to the vcf. [default: False]
  --amplicon            genotype mode for targeted-sequenced samples.
                        In this mode, the default values for `max-reads` and `flank` values are 1000 and 20 respectively [default: False]
  -log, --debug_mode    write the debug messages to log file. [default: False]
  -v, --version         show program's version number and exit
```

The details of each option are given below:

## Reference genome
### `-f or --fasta`
**Expects**: *FILE*<br>
**Default**: *None*<br>
The `-f` or `--fasta` option is used to specify the input FASTA file. The corresponding index file (`.fai`) should be in the same directory. ATaRVa uses [pysam](https://github.com/pysam-developers/pysam)'s `FastaFile` parser to read the input FASTA file.

## Alignment file
### `-b or --bam`
**Expects**: *FILE*<br>
**Default**: *None*<br>
The `-b` or `--bam` option is used to specify one or more input alignment files in the same format. ATaRVa accepts any of the three alignment formats: SAM, BAM, or CRAM. The alignment file should be sorted by coordinates. The format should be specified using the `--format` option. The corresponding index file (`.bai` or `.csi`) should be located in the same directory. An alignment file can be sorted and indexed using the following commands:

```bash
# to sort the alignment file
$ samtools sort -o sorted_output.bam input.bam

# to generate .bai index file
$ samtools index -b sorted_output.bam
```

An alignment file containing at least one of the following tags is preferred for faster processing: `MD` tag, `CS` tag, or a `CIGAR` string with `=/X` operations.

- The CS tag is generated using the --cs option when aligning reads with the [minimap2](https://github.com/lh3/minimap2) aligner. (`--cs=short` is prefered over `--cs=long`)
- The MD tag can be generated using the --MD option in minimap2.

If the alignment files were generated without any of these tags, you can generate the `MD` tag by running the following command to 

```bash
# input: reference genome fasta file & alignment file
# output: an alignment file with MD tag in it

# for generating MD tag
$ samtools calmd -b aln.bam ref.fa > aln_md.bam
```
## Region file
### `-r or --regions`
**Expects**: *FILE*<br>
**Default**: *None*<br>
The `-r` or `--regions` option is used to specify the input TR regions file. ATaRVa requires a sorted, bgzipped BED file of TR repeat regions, along with its corresponding tabix-indexed file. The BED file should contain the following columns:

1. Chromosome name where TR is located
2. Start position of the TR
3. End position of the TR
4. Repeat motif
5. Motif length

Below is an example of a repeat region BED file. **NOTE: The BED file should either have no header or a header that starts with `#` symbol. The .gz and .tbi files should be in same directory**

| #CHROM | START | END | MOTIF | MOTIF_LEN |
|--------|-------|-----|-------|-----------|
| chr1   | 10000 | 10467 | TAACCC | 6    |
| chr1   | 10481 | 10497 | GCCC | 4      |
| chr2   | 10005 | 10173 | CCCACACACCACA | 13 |
| chr2   | 10174 | 10604 | ACCCTA | 6    |
| chr17  | 60483 | 60491 | AGA    | 3    |

To sort, bgzip, and index the BED file, use the following commands:

### Sort
```bash
# input: Unsorted bed file
# output: Sorted bed file

# Sorting the BED file using sort
$ sort -k1,1 -k2,2n input.bed > sorted_output.bed
# or using bedtools
$ bedtools sort -i input.bed > sorted_output.bed
```
### Bgzip
```bash
# input: Sorted bed file
# output: bgzipped bed file

# To keep the original file unchanged and generate separate gz file
$ bgzip -c sorted_output.bed > sorted_output.bed.gz
# or to compress the original file; converts sorted_output.bed to sorted_output.bed.gz
$ bgzip sorted_output.bed
```
### Index
```bash
# input: bgzipped bed file
# output: tabix indexed file (.tbi)

# install samtools to use tabix
$ tabix -p bed sorted_output.bed.gz
```

### `--format`
**Expects**: *STRING*<br>
**Default**: *bam*<br>
This option sets the format of the alignment file. The default format is BAM. Specify the input format as `sam` for SAM files, `cram` for CRAM files, or `bam` for BAM files.  

### `-q or --map-qual`
**Expects**: *INTEGER*<br>
**Default**: *5*<br>
Minimum mapping quality for the reads to be considered. All reads with a mapping quality below the specified value will be excluded during genotyping.

### `--contigs`
**Expects**: *STRING*<br>
**Default**: *None*<br>
Specify the chromosome(s) for genotyping; repeat loci on all other chromosomes will be skipped. If no chromosomes are mentioned, repeats on all chromosomes in the BED file will be genotyped. eg: `--contigs chr1 chr12 chr22` will genotype only the repeat loci in these mentioned chromosomes in the BED file.

### `--min-reads`
**Expects**: *INTEGER*<br>
**Default**: *10*<br>
Minimum number of the supporting reads required to genotype a locus. If the number of reads is less than this value, the locus will be skipped.

### `--max-reads`
**Expects**: *INTEGER*<br>
**Default**: *100*<br>
Maximum number of supporting reads allowed for a locus to be genotyped. If the number of reads exceeds this limit, only this specified number of reads will be used for genotyping the locus.

### `--snp-dist`
**Expects**: *INTEGER*<br>
**Default**: *3000*<br>
Maximum base pair (bp) distance from the flanks of the repeat locus to fetch SNPs from each read considered for phasing.

### `--snp-count`
**Expects**: *INTEGER*<br>
**Default**: *3*<br>
Maximum number of SNPs to be used for read clustering and phasing.

### `--snp-qual`
**Expects**: *INTEGER*<br>
**Default**: *13*<br>
Minimum Q value of the SNPs to be used for phasing.

### `--flank`
**Expects**: *INTEGER*<br>
**Default**: *10*<br>
The number of base pairs in the flanking regions to be used for realignment.

### `--snp-read`
**Expects**: *FLOAT*<br>
**Default**: *0.2*<br>
Minimum fraction of SNPs in the supporting reads of the repeat locus allowed for phasing.

### `--phasing-read`
**Expects**: *FLOAT*<br>
**Default**: *0.4*<br>
Minimum fraction of reads required in both clusters relative to the total supporting reads for the repeat locus after phasing.

### `-o or --vcf`
**Expects**: *STRING (to be used as filename)*<br>
**Default**: *Input Alignment Filename + .vcf*<br>
If this option is not provided, the default output filename will be the same as the input alignment filename, with its extension replaced with '.vcf'. For example, if the input filename is `input.bam`, the default output filename will be `input.vcf`. If the input filename does not have any extension, .vcf will be appended to the filename.
Each entry includes the fields specified in the [Variant Calling Format (VCF)](https://samtools.github.io/hts-specs/VCFv4.3.pdf), as described in the table below.
|     FIELD     |           DESCRIPTION           | 
|---------------|---------------------------------|
| CHROM | Chromosome that contains the repeat region |
| POS | Start position of the repeat region |
| ID |  Region identifier (set to '.') |
| REF | Reference sequence of the repeat region |
| ALT | Sequence of the repeat alleles in the sample |
| QUAL | Quality score of the genotype (set to '0') |
| FILTER | Filter status (PASS, LESS_READS) |
| INFO | Information about the TR region |
| FORMAT | Data type of the genotype information |
| SAMPLE | Values of the genotype information for the TR region |

#### INFO fields
The `INFO` field describes the general structure of the repeat region and includes the following details:
|     INFO      |           DESCRIPTION           | 
|---------------|---------------------------------|
| AC | Total number of respective ALT alleles in called genotypes |
| AN | Total number of alleles in called genotypes |
| MOTIF | Motif of the repeat region |
| END | End position of the repeat region |
| ID  | Tag fetched form the extra column in BED file |

**NOTE: The `ID` tag name depends on the optional column name in the BED file. If the BED file does not have a header, then the tag will be ID.**

#### FORMAT fields
The `FORMAT` fields and their values are provided in the last two columns of the VCF file, containing information about each genotype call. These columns include the following fields:  
|     FORMAT      |           DESCRIPTION           | 
|-----------------|---------------------------------|
| GT | Genotype of the sample |
| AL | Length of the alleles in base pairs |
| SD | Number of supporting reads for each alleles |
| DP | Number of the supporting reads for the repeat locus |
| SN | Number of SNPs used for phasing |
| SQ | Phred-scale qualities of the SNPs used for phasing |  
| DS | Motif decomposed sequence of the alternate alleles |

**NOTE: Loci missing in the VCF either have no reads mapped to them, contain reads that do not fully enclose the repeat region, or have reads with low mapping quality (mapQ).**

### `--karyotype`
**Expects**: *STRING*<br>
**Default**: *XX*<br>
Karyotype of the samples eg. XX or XY.

### `-t or --threads`
**Expects**: *INTEGER*<br>
**Default**: *1*<br>
Number of threads to use for the process.

### `--haplotag`
**Expects**: *STRING*<br>
**Default**: *None*<br>
Specify the haplotype tag to utilize phased information for genotyping. eg `HP`

### `--decompose`
Performs motif-decomposition on ALT sequences.<br>
**NOTE: Only applicable for motif length <= 10**

### `--amplicon`
genotyping mode for targeted sequencing data. In this mode, the default values of `--max-reads` & `--flank` are 1000 & 20 respectively.

### `-v or --version`
Prints the version info of ATaRVa.

## Examples
The following examples assume the input reference genome is in `FASTA` format and is named ref.fa, the alignment file is in `BAM` format and is named input.bam, and the TR regions file is in `BED` format and is named regions.bed.gz.

### Basic usage
To run ATaRVa with default parameters, use the following command:
```bash
$ atarva -f ref.fa --bam input.bam -r regions.bed.gz
```
### With karyotype
To run ATaRVa with sex chromosome karyotype, use the following command:
```bash
$ atarva -f ref.fa --bam input.bam -r regions.bed.gz --karyotype XY
```
With multiple bams:
```bash
$ atarva -f ref.fa --bam input1.bam input2.bam -r regions.bed.gz --karyotype XY XX
```
### With haplotag
To run ATaRVa on haplotagged alignment file, use the following command:
```bash
$ atarva -f ref.fa --bam input.bam -r regions.bed.gz --haplotag HP
```
### With amplicon
To run ATaRVa on targeted sequencing file, use the following command:
```bash
$ atarva -f ref.fa --bam input.bam -r regions.bed.gz --amplicon
```
### Stringent parameter usage
To run ATaRVa with stringent parameters, use the following command:
```bash
$ atarva -q 20 --snp-count 5 --snp-qual 25 --min-reads 20 -t 32 -fi ref.fa --bam input.bam -r regions.bed.gz
# The above command with --snp-count 5 will use a maximum of five heterozygous SNPs to provide accurate genotypes, but only when phasing is based on SNPs and not on length.
```
### Genotyping TRs from specific chromosome/s
To genotype TRs from specific chromosomes only, run ATaRVa with the following command:
```bash
$ atarva --contigs chr9 chr15 chr17 chrX -t 32 -f ref.fa --bam input.bam -r regions.bed.gz
```
### For input alignment file other than `bam`
```bash
# input cram file
$ atarva --format cram -f ref.fa --bam input.cram -r regions.bed.gz

# input sam file
$ atarva --format sam -f ref.fa --bam input.sam -r regions.bed.gz
```
### Usage in docker
To run ATaRVa in docker container, use the following command:
```bash
$ docker run -i -t --rm -v /path_of_necessary_files/:/folder_name atarva:latest -f /folder_name/ref.fa --bam /folder_name/input.bam -r /folder_name/regions.bed.gz
``` 

In all the above examples, the output of ATaRVa is saved to input.vcf unless -o is specified.

## Changelog
### v0.3.0 (current)
* Added `--amplicon` mode for targeted sequencing data
* Added function to convert eqx read sequence
* Improved Outlier cleaning in K-Means clustering
* Implemented De-novo motif identification in motif-decomposition
* Added optional tag `ID` in INFO field if BED input has additional column

### v0.2.0
* Added `--haplotag` argument to enable the use of haplotag information for genotyping.
* Fixed bugs in SNP-based clustering.
* Replaced the use of the mode function with a consensus-based approach for final allele derivation.
* Removed `PC` tag from the FORMAT field of the output VCF.

### v0.1.2
* Modified input arguments.

### v0.1.1
* Added a Mac OS compatible <code>.so</code> file.

### v0.1
* First release.

## Analysis script
All scripts used for analysis are provided in [ATaRVa_Manuscript](https://github.com/SowpatiLab/ATaRVa_Manuscript)

## Citation
If you find ATaRVa useful for your research, please cite it as follows:

ATaRVa: Analysis of Tandem Repeat Variation from Long Read Sequencing data  
_Abishek Kumar Sivakumar, Sriram Sudarsanam, Anukrati Sharma, Akshay Kumar Avvaru, Divya Tej Sowpati_ <br>
_BioRxiv_, **doi:** https://doi.org/10.1101/2025.05.13.653434

## Contact
For queries or suggestions, please contact:

Divya Tej Sowpati - tej at csirccmb dot org

Abishek Kumar S - abishekks at csirccmb dot org

Akshay Kumar Avvaru - avvaruakshay at gmail dot com
