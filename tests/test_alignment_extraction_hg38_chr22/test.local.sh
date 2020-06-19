#!/bin/bash

# Tear down test environment
cleanup () {
    rc=$?
    rm -rf .snakemake/
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
    --configfile="config.yml" \
    --cores=4 \
    --printshellcmds \
    --rerun-incomplete \
    --use-singularity \
    --singularity-args="--bind ${PWD},${PWD}/../../docker/,${PWD}/../" \
    --singularity-prefix "../.snakemake/singularity" \
    --verbose

# Check md5 sum of some output files
md5sum --check "expected_output.md5"

# Checksum file generated with
# find results/ \
#     -type f \
#     -name \*\.net.axt \
# find results/ \
#     -type f \
#     -name \*\.nh \
# manual addition of other files.
# md5sum $(cat expected_output.files) > expected_output.md5
