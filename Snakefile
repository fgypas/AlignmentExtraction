import os


localrules: download_ucsc_tree, 
            download_pairwise_alignments_from_ucsc, 
            uncompress_pairwise_alignments, 
            download_genome, 
            compress_MIRZAG_alignments,
            finish


onstart:
    print("Starting workflow...")
    if cluster_config:
        print("Creating cluster log directory.")
        os.makedirs(
            os.path.join(
                os.getcwd(),
                os.path.dirname(cluster_config['__default__']['out']),
            ),
            exist_ok=True)

rule finish:
    input:
        mln = os.path.join(config["output_dir"], "alignments.mln"),
        pgln = os.path.join(config["output_dir"], "alignments.pgln"),
        mirza_tar_gz = os.path.join(config["output_dir"], "mirzag.tar.gz")


#####################
# Prepare annotation
#####################

rule download_ucsc_tree:
    output:
        tree = os.path.join(config["output_dir"], "tree.nh")
    params:
        tree = config["tree"]
    singularity:
        "docker://zavolab/zavolab_minimal:1"
    log:
        os.path.join(config["local_log"], "download_ucsc_tree.log")
    shell:
        "(wget \
        --output-document {output.tree} \
        {params.tree}) &> {log}"

rule extract_assembly_versions:
    input:
        script = os.path.join(config["scripts"], "python","extract_assembly_versions.py"),
        tree = os.path.join(config["output_dir"], "tree.nh")
    output:
        assemblies = os.path.join(config["output_dir"], "assemblies.txt"),
        updated_tree = os.path.join(config["output_dir"], "updated_tree.nh")
    params:
        reference = config["genome"],
        organisms = ",".join(list(config["organisms"])),
        remote_root = config["remote_root"]
    singularity:
        "docker://zavolab/python:3.6.5"
    log:
        os.path.join(config["local_log"], "extract_assembly_versions.log")
    shell:
        "({input.script} \
        --reference {params.reference} \
        --species_to_download {params.organisms} \
        --remote_dir {params.remote_root} \
        --phylogenetic_tree {input.tree} \
        --out_tree {output.updated_tree} \
        --out_assemblies {output.assemblies} \
        --verbose) &> {log}"


rule prune_tree:
    input:
        tree = os.path.join(config["output_dir"], "updated_tree.nh"),
        organisms = os.path.join(config["output_dir"], "assemblies.txt")
    output:
        tree = os.path.join(config["output_dir"], "tree.prunned.nh")
    params:
        organism = config["genome"]
    singularity:
        "docker://zavolab/prune_tree:1.0.0"
    log:
        os.path.join(config["local_log"], "prune_tree.log")
    shell:
        "(prune_tree.R \
        --input_tree {input.tree} \
        --reference_organism {params.organism} \
        --organisms {input.organisms} \
        --output_tree {output.tree}\
        --verbose) &> {log}"


rule download_pairwise_alignments_from_ucsc:
    input:
        tree = os.path.join(config["output_dir"], "tree.prunned.nh"),
        assemblies = os.path.join(config["output_dir"], "assemblies.txt"),
        script = os.path.join(config["scripts"], "python","download_pairwise_alignments_from_ucsc.py")
    params:
        genome_link = config["genome_link"],
        genome = config["genome"],
        organism_to_download = "{organism}",
        alignments_directory = os.path.join(config["output_dir"], "alignments"),
    output:
        pairwise_alignment = temp(os.path.join(config["output_dir"], "alignments", config["genome"] + "_to_{organism}", config["genome"] + ".{organism}.net.axt.gz"))
    singularity:
        "docker://zavolab/python:3.6.5"
    log:
        os.path.join(config["local_log"], "download_pairwise_alignments_from_ucsc_{organism}.log")
    shell:
        "({input.script} \
        --organism_link {params.genome_link} \
        --organism {params.genome} \
        --organism_to_download {params.organism_to_download} \
        --assemblies {input.assemblies} \
        --out {params.alignments_directory} \
        --verbose) &> {log}"


rule uncompress_pairwise_alignments:
    input:
        pairwise_alignment = os.path.join(config["output_dir"], "alignments", config["genome"] + "_to_{organism}", config["genome"] + ".{organism}.net.axt.gz")
    output:
        pairwise_alignment = temp(os.path.join(config["output_dir"], "alignments", config["genome"] + "_to_{organism}", config["genome"] + ".{organism}.net.axt"))
    singularity:
        "docker://zavolab/zavolab_minimal:1"
    log:
        os.path.join(config["local_log"], "uncompress_pairwise_alignments_{organism}.log")
    shell:
        "(gunzip < {input.pairwise_alignment} > {output.pairwise_alignment}) &> {log}"


rule split_pairwise_alignment_by_chromosome:
    input:
        pairwise_alignment = os.path.join(config["output_dir"], "alignments", config["genome"] + "_to_{organism}", config["genome"] + ".{organism}.net.axt"),
        script = os.path.join(config["scripts"], "python", "split_pairwise_alignments_by_chromosome.py")
    output:
        done = os.path.join(config["output_dir"], "alignments", config["genome"] + "_to_{organism}/Done")
    params:
        out = os.path.join(config["output_dir"], "alignments", config["genome"] + "_to_{organism}"),
    singularity:
        "docker://zavolab/python:3.6.5"
    log:
        os.path.join(config["local_log"], "split_pairwise_alignment_by_chromosome_{organism}.log")
    shell:
        "({input.script} \
        --alignment {input.pairwise_alignment} \
        --out {params.out} \
        --verbose) &> {log}"


rule download_genome:
    output:
        genome = os.path.join(config["output_dir"], config["genome"]+".fa")
    params:
        genome_remote = config["genome_remote"],
        genome_compressed = os.path.join(config["output_dir"], config["genome"]+".fa.gz"),
    singularity:
        "docker://zavolab/zavolab_minimal:1"
    log:
        os.path.join(config["local_log"], "download_genome.log")
    shell:
        "(wget {params.genome_remote} -O {params.genome_compressed}; \
        gunzip {output.genome}) &> {log}"


rule index_genome:
    input:
        genome = os.path.join(config["output_dir"], config["genome"]+".fa")
    output:
        gmap_index = directory(os.path.join(config["output_dir"], "gmap_index"))
    params:
        genome = config["genome"]
    singularity:
        'docker://zavolab/gmap:2018-05-11'
    log:
        os.path.join(config["local_log"], "index_genome.log")
    shell:
        "(gmap_build \
        -D {output.gmap_index} \
        -d {params.genome} \
        -s numeric-alpha \
        {input.genome}) &> {log}"



#################
# Process data
#################

rule map_to_genome:
    input:
        gmap_index = os.path.join(config["output_dir"], "gmap_index"),
        sequences = config["sequences"]
    output:
        psl = os.path.join(config["output_dir"], "output.psl")
    params:
        genome = config["genome"]
    singularity:
        'docker://zavolab/gmap:2018-05-11'
    threads:    8
    log:
        os.path.join(config["local_log"], "map_to_genome.log")
    shell:
        "(gmap \
        --dir={input.gmap_index} \
        -d {params.genome} \
        --format=1 \
        -n 1 \
        -z sense_filter \
        --nthreads={threads} \
        < {input.sequences} > {output.psl}) &> {log}"


rule convert_psl:
    input:
        psl = os.path.join(config["output_dir"], "output.psl"),
        script = os.path.join(config["scripts"], "python", "rg_psl_to_match.py")
    output:
        match_tsv = os.path.join(config["output_dir"], "output.match.tab"),
    singularity:
        "docker://zavolab/python:3.6.5"
    log:
        os.path.join(config["local_log"], "convert_psl.log")
    shell:
        "({input.script} \
        --input {input.psl} \
        --output {output.match_tsv}) &> {log}"


checkpoint split:
    #Note: here there is a problem that I cannot specify {log} because of the
    #dynamic wildcard. Open issue on snakemake
    input:
        match_tsv = os.path.join(config["output_dir"], "output.match.tab"),
        script = os.path.join(config["scripts"], "python", "rg_split_match_tab.py")
    output:
        out_dir = directory(os.path.join(config["output_dir"], "split"))
    params:
        batch_size = config["batch_size"]
    singularity:
        "docker://zavolab/python:3.6.5"
    # log:
    #     os.path.join(config["local_log"], "split.log")
    shell:
        "({input.script} \
        --input {input.match_tsv} \
        --batch-size {params.batch_size} \
        --output-dir {output.out_dir})"


rule assemble_utrs:
    input:
        match_batches = os.path.join(config["output_dir"], "split/output.match.tab_part_{batchid}"),
        done = expand(os.path.join(config["output_dir"],"alignments", config["genome"] + "_to_{organism}/Done"), organism=config["organisms"]),
        script = os.path.join(config["scripts"], "perl", "assembleUTRsFromPairwiseConsMultiRemovedComments.pl")
    output:
        out_dir = directory(os.path.join(config["output_dir"], "assemble_utrs/part_{batchid}/")),
        mln = os.path.join(config["output_dir"], "assemble_utrs/part_{batchid}_Reg-to-VWF.mln")
    params:
        genome = config["genome"],
        alignments_directory = os.path.join(config["output_dir"],"alignments"),
        organisms = ",".join(config["organisms"])
    singularity:
        "docker://zavolab/ucsc_pairwise_alignments_custom_scripts_perl:0.1"
    log:
        os.path.join(config["local_log"], "assemble_utrs_{batchid}.log")
    shell:
        "({input.script} \
        {params.alignments_directory} \
        {params.genome} \
        {params.organisms} \
        {input.match_batches} \
        {output.out_dir} && \
        bash -c \'mergeAssembledUTRs.pl {output.out_dir}* \' \
        > {output.mln}) &> {log}"


rule align_pairwise_multi_org:
    input:
        mln = os.path.join(config["output_dir"], "assemble_utrs/part_{batchid}_Reg-to-VWF.mln"),
        sequences = config["sequences"],
        script = os.path.join(config["scripts"], "perl", "alignPairwiseMultiOrg.pl")
    output:
        pgln = os.path.join(config["output_dir"], "align_pairwise_multi_org/part_{batchid}_Reg-to-VWF.pgln")
    params:
        genome = config["genome"]
    singularity:
        "docker://zavolab/ucsc_pairwise_alignments_custom_scripts_perl:0.1"
    log:
        os.path.join(config["local_log"], "align_pairwise_multi_org_{batchid}.log")
    shell:
       "({input.script} \
       {input.mln} \
       {input.sequences} \
       {params.genome} \
       > {output.pgln}) &> {log}"


def aggregate_input_concat_alignments(wildcards):
    ''' aggregate file names of random number of files '''
    cp_out = checkpoints.split.get(**wildcards).output[0]
    return expand(os.path.join(config["output_dir"], "assemble_utrs/part_{batchid}_Reg-to-VWF.mln"),
        batchid = glob_wildcards(os.path.join(cp_out, "output.match.tab_part_{batchid}")).batchid)


rule concatenate_alignments:
    input:
        mln_batches = aggregate_input_concat_alignments
    output:
        mln = os.path.join(config["output_dir"], "alignments.mln")
    log:
        os.path.join(config["local_log"], "concatenate_alignments.log")
    shell:
        '(cat {input.mln_batches} > {output.mln}) &> {log}'


def aggregate_input_alignments_final(wildcards):
    ''' aggregate file names of random number of files '''
    cp_out = checkpoints.split.get(**wildcards).output[0]
    return expand(os.path.join(config["output_dir"], "align_pairwise_multi_org/part_{batchid}_Reg-to-VWF.pgln"),
        batchid = glob_wildcards(os.path.join(cp_out, "output.match.tab_part_{batchid}")).batchid)


rule concatenate_alignments_final:
    input:
        pgln_batches = aggregate_input_alignments_final
    output:
        pgln = os.path.join(config["output_dir"], "alignments.pgln")
    log:
        os.path.join(config["local_log"], "concatenate_alignments_final.log")
    shell:
        '(cat {input.pgln_batches} > {output.pgln}) &> {log}'


checkpoint split_for_MIRZAG:
    input:
        mln = os.path.join(config["output_dir"], "alignments.mln"),
        script = os.path.join(config["scripts"], "python", "rg_divide_alignment_file.py")
    output:
        out_dir = directory(os.path.join(config["output_dir"], "mirzag"))
    singularity:
        "docker://zavolab/python:3.6.5"
    # log:
    #     os.path.join(config["local_log"], "split_for_MIRZAG.log")
    shell:
        "({input.script} \
        --mln {input.mln} \
        --output-dir {output.out_dir})"


def aggregate_input(wildcards):
    ''' aggregate file names of random number of files '''
    cp_out = checkpoints.split_for_MIRZAG.get(**wildcards).output[0]
    return cp_out


rule compress_MIRZAG_alignments:
    input:
        mirzag_batches = aggregate_input
    output:
        mirza_tar_gz = os.path.join(config["output_dir"], "mirzag.tar.gz")
    params:
        mirzag = os.path.join(config["output_dir"], 'mirzag')
    log:
        os.path.join(config["local_log"], "compress_MIRZAG_alignments.log")
    shell:
        "(tar -zcf {output.mirza_tar_gz} -C {params.mirzag} .) &> {log}"


onsuccess:
    print("Workflow finished, no error.")
