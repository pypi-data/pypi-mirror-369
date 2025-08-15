# schic

schic is a Python package for analyzing ONT cDNA sequencing data. It provides a set of modules for identifying new genes and isoforms

# Table of Contents
<!-- TOC -->

- [schic](#schic)
- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Requirements](#requirements)
- [schic modules](#schic-modules)
    - [schic whitelist](#schic-whitelist)
    - [Usage](#usage)
    - [schic extract](#schic-extract)
    - [Usage](#usage)
    - [schic cutadapt](#schic-cutadapt)
    - [Usage](#usage)
    - [schic contacts](#schic-contacts)
    - [Usage](#usage)
- [Docker](#docker)
- [Conda Environment](#conda-environment)
- [Cite schic](#cite-schic)

<!-- /TOC -->

# Overview

schic 

# Requirements

1. Python 3.10+
2. cutadapt 2.10+
3. 


# schic modules
schic provides a set of modules for analyzing sc-hic data. The modules are:

- whitelist
- extract
- cutadapt
- contacts
- report

## schic whitelist

## Usage

```bash
bc_pattern='(?P<discard_1>ACATGGCTACGATCCGACTTTCTGCG)(?P<cell_1>.{10})(?P<discard_2>CCTTCC)(?P<cell_2>.{10})(?P<discard_3>TCGTCGGCAGCGTCAGATGTGTATA)(?P<umi_1>.{1}).*'

schic whitelist \
    --bc-pattern=${bc_pattern} \
    --stdin ../input/${i}/${i}_R1.fastq.gz \
    --set-cell-number=5000 \
    --plot-prefix=${i}_whitelist \
    --stdout=${i}_whitelist.txt
```

## schic extract

## Usage

```bash
bc_pattern='(?P<discard_1>ACATGGCTACGATCCGACTTTCTGCG)(?P<cell_1>.{10})(?P<discard_2>CCTTCC)(?P<cell_2>.{10})(?P<discard_3>TCGTCGGCAGCGTCAGATGTGTATA)(?P<umi_1>.{1}).*'

schic extract \
    --bc-pattern=${bc_pattern} \
    --stdin ../input/${i}/${i}_R1.fastq.gz \
    --stdout ${i}_R1.extracted.fastq.gz \
    --read2-in ../input/${i}/${i}_R2.fastq.gz \
    --read2-out ${i}_R2.extracted.fastq.gz \
    --whitelist=${REF}/barcodes/whitelist.txt
```

## schic cutadapt

## Usage

```bash
schic cutadapt \
    --read1 ${i}_R1.extracted.fastq.gz \
    --read2 ${i}_R2.extracted.fastq.gz \
    --read1-out ${i}_R1.trimmed.fastq.gz \
    --read2-out ${i}_R2.trimmed.fastq.gz

```

## schic contacts

## Usage

```bash

schic contacts \
    

```

# Docker

If the user has docker installed, the following command can be used to run the pipeline in a docker container:

```
docker run -v /path/to/data:/data -it schic/schic:latest /bin/bash
```

# Conda Environment

If the user has conda installed, the following command can be used to create a conda environment for schic:

1. Install conda
2. Create a new conda environment: `conda create -n schic python=3.10`
3. Activate the environment: `conda activate schic`
4. Install the required packages: `conda install -c bioconda minimap2 samtools bedtools flair tombo mines`
5. Install the required python packages: `pip install pandas numpy scipy sklearn matplotlib seaborn pysam`
6. Clone the schic repository: `git clone https://github.com/epibiotek/schic.git`

# Cite schic

If you use schic in your research, please cite the following paper: