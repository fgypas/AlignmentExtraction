#!/bin/bash

# Tear down test environment
cleanup () {
    rc=$?
    rm -rf .snakemake
    cd $user_dir
    echo "Exit status: $rc"
}
trap cleanup EXIT

# Set up test environment
set -eo pipefail  # ensures that script exits at first command that exits with non-zero status
set -u  # ensures that script exits when unset variables are used
set -x  # facilitates debugging by printing out executed commands
user_dir=$PWD
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd $script_dir

# Run tests
snakemake \
    --snakefile="../../Snakefile" \
    --configfile="../test_alignment_extraction_hg38_chr22/config.yml" \
    --rulegraph \
    --printshellcmds \
    --dryrun \
    --verbose \
    | dot -Tsvg > "../../images/rule_graph_alignment_extraction_hg38_chr22.svg"