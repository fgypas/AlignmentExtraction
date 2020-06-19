#!/bin/bash

# Get exit status
cleanup () {
    rc=$?
    cd $user_dir
    echo "Exit status: $rc"
}
trap cleanup EXIT

# Set up run environment
set -eo pipefail  # ensures that script exits at first command that exits with non-zero status
set -u  # ensures that script exits when unset variables are used
set -x  # facilitates debugging by printing out executed commands
user_dir=$PWD
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd $script_dir

# Run
snakemake \
    --snakefile="../Snakefile" \
    --configfile="config_template.yml" \
    --cluster-config="input_files/cluster.json" \
    --cluster="sbatch --cpus-per-task={cluster.threads} --mem={cluster.mem} --qos={cluster.queue} --time={cluster.time} --job-name={cluster.name} -o {cluster.out} -p scicore" \
    --cores=256 \
    --printshellcmds \
    --rerun-incomplete \
    --use-singularity \
    --singularity-args="--bind ${PWD},${PWD}/../docker/" \
    --verbose