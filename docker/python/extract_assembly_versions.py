#!/usr/bin/env python

__version__ = "0.1"
__author__ = "Mihaela Zavolan"
__contact__ = "mihaela.zavolan@unibas.ch"
__doc__ = "Extract the assembly versions for a set of species for which pairwise genome alignments with a reference are available"

# _____________________________________________________________________________
# -----------------------------------------------------------------------------
# import needed (external) modules
# -----------------------------------------------------------------------------

import sys
import os
import wget
from argparse import ArgumentParser, RawTextHelpFormatter
import random
import re

# _____________________________________________________________________________
# -----------------------------------------------------------------------------
# Main function
# -----------------------------------------------------------------------------


def main():
    """ Main function """

    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawTextHelpFormatter
    )

    parser.add_argument(
        "--reference",
        dest="reference",
        help="Assembly version for the reference organism (e.g. hg38, hg19, mm10)",
        required=True,
        metavar="FILE"
    )

    parser.add_argument(
        "--species_to_download",
        dest="species_to_download",
        help="UCSC code for species to use in pairwise alignments",
        required=True
    )

    parser.add_argument(
        "--remote_dir",
        dest="remote_dir",
        help="UCSC directory where pairwise alignments should be found",
        required=True
    )

    parser.add_argument(
        "--phylogenetic_tree",
        dest="phylogenetic_tree",
        help="Multiz tree file from UCSC",
        required=True
    )

    parser.add_argument(
        "--out_tree",
        dest="out_tree",
        help="path to output tree",
        required=True,
        metavar="FILE"
    )

    parser.add_argument(
        "--out_assemblies",
        dest="out_assemblies",
        help="path to output assemblies",
        required=True,
        metavar="FILE"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        required=False,
        help="Verbose"
    )

    parser.add_argument(
        '--version',
        action='version',
        version=__version__
    )

    # _________________________________________________________________________
    # -------------------------------------------------------------------------
    # get the arguments
    # -------------------------------------------------------------------------
    try:
        options = parser.parse_args()
    except(Exception):
        parser.print_help()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)


    refAssembly = options.reference
    speciesList = options.species_to_download

    #get the content of the directory containing pairwise alignments
    output_dir = os.path.dirname(options.phylogenetic_tree)
    tmp_file = "tmp" + str(random.random())
    tmp_file = os.path.join(output_dir, tmp_file)
    try:
        wget.download(options.remote_dir, tmp_file)
    except:
        sys.stderr.write("Could not download " + options.remote_dir + os.linesep)

    #parse the html and identify all directories with pairwise alignments
    #they look like this <a href="vsMm10/">vsMm10/</a>
    dirRe = re.compile(r'<a\s+href="vs([a-zA-Z]+\d+)/"')
    
    #usage:
    #python extract_assembly_versions.py 
    #--reference hg38 
    #--species_to_download "rheMac,mm,bosTau,felCat,galGal,rn" 
    #--remote_dir w 
    #--phylogenetic_tree hg38.100way.nh 
    #--out_tree [OUTPUTDIR]/treename.nh
    #--out_assemblies [OUTPUTDIR]/assemblies.txt

    #for each of the species in the speciesList
    #identify the most recent assembly version (highest index value)
    species = speciesList.split(',')
    versions = {}
    with open(tmp_file) as f:
        #find all occurrences of directories we may be interested in
        dirs = dirRe.findall(f.read())
        for dir in dirs:
            m = re.match(r'([a-zA-Z]+)(\d+)', dir)
            #in the directory name, first letter of assembly name is cap, in the species tree is lower case
            assembly = m.group(1)
            assembly = assembly[0].lower() + assembly[1:]
            version = int(m.group(2))
            if(assembly in species):
                if(assembly in versions.keys()):
                    if(versions[assembly] < version):
                        versions[assembly] = version
                else:
                    versions[assembly] = version
                        
    #cleanup: remove the temporary file
    os.remove(tmp_file)
    
    #read phylogenetic tree and check that the species
    #for which we found alignments are represented
    assemblyRe = re.compile(r'[^a-z]([a-zA-Z]+)\d+:')
    foundSpecies = []
    treeContent = ''

    #read tree
    with open(options.phylogenetic_tree) as f:
        treeContent = f.read()

    #find represented species
    treeSpecies = assemblyRe.findall(treeContent)
    for val in species:
        if val in treeSpecies:
            foundSpecies.append(val)

    #save corresponding assembly versions
    foundAlignments = []
    for val in foundSpecies:
        foundAlignments.append(val + str(versions[val]))
        
    #output the list of assembly versions for which we will download alignments
    #in a format like this
    #organisms: ["rheMac3","mm10","bosTau8","felCat8","galGal4","rn6"]
    species_file = open(options.out_assemblies, 'w')
    species_file.write(",".join(foundAlignments))
    species_file.close()
    
    #write a new phylogenetic tree file that contains,
    #for the species of interest,
    #the assembly version that we will use
    newTreeContent = treeContent
    for val in foundSpecies:
        replString = val + str(versions[val])
        searchString = val + "\d+"
        newTreeContent = re.sub(searchString, replString, newTreeContent)

    #write out the tree
    new_tree_file = open(options.out_tree, 'w')
    new_tree_file.write(newTreeContent)
    new_tree_file.close()

# _____________________________________________________________________________
# -----------------------------------------------------------------------------
# Call the Main function and catch Keyboard interrups
# -----------------------------------------------------------------------------


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write("User interrupt!" + os.linesep)
        sys.exit(0)
