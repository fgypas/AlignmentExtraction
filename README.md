# Alignment Extraction

## Installation

### Cloning the repository

Traverse to the desired path on your file system, then clone the repository and
move into it with:

```bash
git clone ssh://git@git.scicore.unibas.ch:2222/zavolan_group/pipelines/rhea.git
cd rhea
```

### Installing Conda

Workflow dependencies can be conveniently installed with the [Conda][conda]
package manager. We recommend that you install
[Miniconda][miniconda-installation] for your system (Linux). Be sure to select
Python 3 option. The workflow was built and tested with `miniconda 4.7.12`.
Other versions are not guaranteed to work as expected.

### Installing dependencies

For improved reproducibility and reusability of the workflow,
each individual step of the workflow runs in its own [Singularity][singularity]
container. As a consequence, running this workflow has very few
individual dependencies. It does, however, require Singularity to be installed
on the system running the workflow. As the functional installation of
Singularity requires root privileges, and Conda currently only provides
Singularity for Linux architectures, the installation instructions are
slightly different depending on your system/setup:

#### For most users

If you do *not* have root privileges on the machine you want to run the
workflow on *or* if you do not have a Linux machine, please [install
Singularity][singularity-install] separately and in privileged mode, depending
on your system. You may have to ask an authorized person (e.g., a systems
administrator) to do that. This will almost certainly be required if you want
to run the workflow on a high-performance computing (HPC) cluster. We have
successfully tested the workflow with the following Singularity versions:

- `v2.4.5`
- `v2.6.2`
- `v3.5.2`

After installing Singularity, install the remaining dependencies with:

```bash
conda env create -f install/environment.yml
```

#### As root user on Linux

If you have a Linux machine, as well as root privileges, (e.g., if you plan to
run the workflow on your own computer), you can execute the following command
to include Singularity in the Conda environment:

```bash
conda env create -f install/environment.root.yml
```

### Activate environment

Activate the Conda environment with:

```bash
conda activate rhea
```

### Installing non-essential dependencies

Most tests have additional dependencies. If you are planning to run tests, you
will need to install these by executing the following command _in your active
Conda environment_:

```bash
conda env update -f install/environment.dev.yml
```

## Testing the installation

We have prepared several tests to check the integrity of the workflow, its
components and non-essential processing scripts. These can be found in
subdirectories of the `tests/` directory.

> Note that for this and other tests to complete without issues,
> [additional dependencies](#installing-non-essential-dependencies) need to be
> installed.

## Preparing annotations

Select organism (If the organism is missing you can use as template on of the existing ones)
```bash
cd AlignmentExtraction/prepare_annotation/snakemake/<prefered organism>
```

Fill in the config.yaml

Create a dag (optional)
```bash
bash create_snakemake_flowchart.sh
```

Run the pipeline locally
```bash
bash run_on_local.sh
```

or in a cluster (tested with slurm)
```bash
bash run_on_cluster.sh
```

## Generating mirzag input files

Once the previous step is complete (prepare_annotation) go to

```bash
../../runs/<prefared organism>/snakemake/

```

<!-- ## Build Singularity containers from Docker

Please note that it may not run when using OSX. See below on how to copy data.

```bash
docker run -d -p 5000:5000 --restart=always --name registry registry:2 # run it once
cd docker/python/
docker build -t zavolanlab/alignment-extraction-python:1 .
docker image tag zavolanlab/alignment-extraction-python:1 localhost:5000/zavolanlab/alignment-extraction-python:1
docker push localhost:5000/zavolanlab/alignment-extraction-python:1
SINGULARITY_NOHTTPS=true singularity pull docker://localhost:5000/zavolanlab/alignment-extraction-python:1
cd ../perl
docker build -t zavolanlab/alignment-extraction-perl:1 .
docker image tag zavolanlab/alignment-extraction-perl:1 localhost:5000/zavolanlab/alignment-extraction-perl:1
docker push localhost:5000/zavolanlab/alignment-extraction-perl:1
SINGULARITY_NOHTTPS=true singularity pull docker://localhost:5000/zavolanlab/alignment-extraction-perl:1
```

## Data for tests

```bash
cp -r /scicore/home/zavolan/gumiennr/Pipelines/jobber/AlignmentExtraction/data/hg19/alignments/ data/hg19/
cp -r /scicore/home/zavolan/gypas/projects/AlignmentExtraction/data/hg19/gmap_index_2018-03-25/ data/hg19/
cp -r /scicore/home/zavolan/gypas/projects/AlignmentExtraction/alignment-extraction-perl-1.img
cp -r /scicore/home/zavolan/gypas/projects/AlignmentExtraction/alignment-extraction-python-1.img
```

Create hard links for testing

```bash
cd tests/hg19/snakemake/
ln ../../../alignment-extraction-python-1.img alignment-extraction-python-1.simg
ln ../../../alignment-extraction-perl-1.img alignment-extraction-perl-1.simg
cd tests/hg19/cwl/
ln ../../../alignment-extraction-python-1.img zavolanlab-alignment-extraction-python-1.img
ln ../../../alignment-extraction-perl-1.img zavolanlab-alignment-extraction-perl-1.img
``` -->
