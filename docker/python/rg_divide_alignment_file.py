#!/usr/bin/env python
"""
Divide the multiple alignment file in mln format into separate transcript files
"""

__date_ = "2014-05-23"
__modification_date__ = "2020-03-28"
__author__ = "Rafal Gumienny"
__update_by__ = "Mihaela Zavolan (mihaela.zavolan@unibas.ch)"
__email__ = "r.gumienny@unibas.ch"
__license__ = "GPL"

# imports
import os
import sys
import itertools
import pickle as cp
from argparse import ArgumentParser

# redefine a functions for writing to stdout and stderr to save some writting
syserr = sys.stderr.write
sysout = sys.stdout.write


def isa_group_separator(line):
    return line=='\n'

def read_mln_to_dict(filetoread):
    data = {}
    with open(filetoread) as f:
        #format of aln file:
        #>description line
        #query seq alnmt
        #target seq algnmt
        for key, block in itertools.groupby(f, isa_group_separator):
            group = list(block)
            if not key:
                tmp = {}
                #parse 3 lines at a time: description, query  alnmt, target alnmt
                #save the info in a dictionary indexed by species
                for i in range(0, len(group)-2, 3):
                    species_name = group[i].rstrip().split(" ")[-1]
                    query_name = group[i].rstrip().split(" ")[0][1:].replace('|', '__')
                    query_alnmt = group[i+1].rstrip()
                    target_alnmt = group[i+2].rstrip()
                    tmp[species_name] = [query_alnmt, target_alnmt]
                #save the data for this query in the central dictionary
                data[query_name] = tmp
    return data

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("-v",
                        "--verbose",
                        dest="verbose",
                        action="store_true",
                        default=False,
                        help="Be loud!")
    parser.add_argument("--mln",
                        dest="mln",
                        help="Alignment file in mln format")
    parser.add_argument("--output-dir",
                        dest="output_dir",
                        help="Directory for the divided files")
    try:
        options = parser.parse_args()
    except Exception:
            parser.print_help()
            sys.exit(1)


    """Main logic of the script"""
    try:
        if options.verbose:
            syserr("Reading alignment file\n")
        multiple_alignment_dict = read_mln_to_dict(options.mln)
    except OSError:
        raise OSError("Cannot open multiple alignment file %s" % options.mln)

    if not os.path.exists(options.output_dir):
        os.makedirs(options.output_dir)

    for name, value in multiple_alignment_dict.items():
        if options.verbose:
            syserr("Saving %s to %s\r" % (name, options.output_dir))
        with open(os.path.join(options.output_dir, name), 'wb') as aln:
            cp.dump(value, aln, protocol=0)
    if options.verbose:
        syserr("\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        syserr("Interrupted by user\n")
        sys.exit(1)
