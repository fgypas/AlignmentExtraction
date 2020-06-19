#!/usr/bin/env python
"""
Convert adjusted PSL file to the match.tab file defined by Jean Hausser
"""

__date__ = "2016-06-21"
__modification_date__ = "2020-03-27"
__author__ = "Rafal Gumienny"
__update_by__ = "Mihaela Zavolan (mihaela.zavolan@unibas.ch)"
__email__ = "r.gumienny@unibas.ch"
__license__ = "GPL"

# imports
import sys
import errno
from contextlib import contextmanager
from argparse import ArgumentParser, RawTextHelpFormatter


# redefine a functions for writing to stdout and stderr to save some writting
syserr = sys.stderr.write
sysout = sys.stdout.write

#auxilliary function to change array offset (0 vs 1)
def minus1(val):
    return val-1

def main():
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument("-v", 
                        "--verbose", 
                        dest="verbose", 
                        action="store_true", 
                        default=False, help="Be loud!")
    parser.add_argument("--input", 
                        dest="input", 
                        default=sys.stdin, 
                        help="Input file in adjusted PSL format. Defaults to sys.stdin.")
    parser.add_argument("--output", 
                        dest="output", 
                        default=sys.stdout, 
                        help="Output file in match.tab format. Defaults to sys.stdout.")
    try:
        options = parser.parse_args()
    except(Exception):
        parser.print_help()
        sys.exit(1)


    """Main logic of the script"""
    all_tr = 0
    written_tr = 0
    with smart_open(options.input, 'r') as psl, smart_open(options.output, 'w') as out:
        for line in psl:
            all_tr += 1
            try:
                l = line.rstrip().split('\t')
                '''psl file format, columns:
                1. matches - Number of bases that match that aren't repeats
                2. misMatches - Number of bases that don't match
                3. repMatches - Number of bases that match but are part of repeats
                4. nCount - Number of "N" bases
                5. qNumInsert - Number of inserts in query
                6. qBaseInsert - Number of bases inserted in query
                7. tNumInsert - Number of inserts in target
                8. tBaseInsert - Number of bases inserted in target
                9. strand - "+" or "-" for query strand. For translated alignments, second "+"or "-" is for target genomic strand.
                10. qName - Query sequence name
                11. qSize - Query sequence size.
                12. qStart - Alignment start position in query
                13. qEnd - Alignment end position in query
                14. tName - Target sequence name
                15. tSize - Target sequence size
                16. tStart - Alignment start position in target
                17. tEnd - Alignment end position in target
                18. blockCount - Number of blocks in the alignment (a block contains no gaps)
                19. blockSizes - Comma-separated list of sizes of each block. If the query is a protein and the target the genome, blockSizes are in amino acids. See below for more information on protein query PSLs.
                20. qStarts - Comma-separated list of starting positions of each block in query
                21. tStarts - Comma-separated list of starting positions of each block in target
                #
                # we need the following:               
                # $10,$14,$9,$18,$19,$20,$21'''
                col_list = [10, 14, 9, 18, 19, 20, 21]
                col_list = list(map(minus1, col_list))
                l = [l[i] for i in col_list]
                name = l[0] #transcript name
                chrom = l[1] #chromosome
                strand = l[2] #strand
                #nblocks = int(l[3]) #nr blocks (exons)
                #l[4] = exon lengths
                #l[5] = exon starts in transcript
                #l[6] = exon starts in genome
                domain = ''
            except KeyError:
                print(name)
                continue
            i = 1
            written_tr += 1
#            for plen, trcoor, gcoor in zip(l[4].split(','), l[5].split(','), l[6].split(','))[:-1]:

            for (plen, trcoor, gcoor) in zip(l[4].split(',')[:-1], l[5].split(',')[:-1], l[6].split(',')[:-1]):
                outtext = "%s%s.%i\t%s\t%i\t%i\t%s\t%i\t%i\n"%(name,
                                                               domain,
                                                               i,
                                                               chrom,
                                                               int(gcoor)+1,
                                                               int(gcoor)+int(plen),
                                                               strand,
                                                               int(trcoor)+1,
                                                               int(trcoor)+int(plen))
                out.write(outtext)
                i+=1
    out.close()
    if options.verbose:
        syserr("Wrote %i sequences out of %i\n" % (written_tr, all_tr))


# this function is also defined in utils but I put it here to avoid
# unnecessary module import that might not be available everywhere as
# it is my own module
@contextmanager
def smart_open(filepath, mode='r'):
    """Open file intelligently depending on the source

    :param filepath: can be both path to file or sys.stdin or sys.stdout
    :param mode: mode can be read "r" or write "w". Defaults to "r"
    :yield: context manager for file handle

    """
    if mode == 'r':
        if filepath is not sys.stdin:
           fh = open(filepath, 'r')
        else:
            fh = filepath
        try:
            yield fh
        except OSError as e:
            if fh is not sys.stdin:
                fh.close()
            elif e.errno == errno.EPIPE:
                pass
        finally:
            if fh is not sys.stdin:
                fh.close()
    elif mode == 'w':
        if filepath is not sys.stdout:
            fh = open(filepath, 'w')
        else:
            fh = filepath
        try:
            yield fh
        finally:
            if fh is not sys.stdout:
                fh.close()
    else:
        raise Exception("No mode %s for file" % mode)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        syserr("Interrupted by user\n")
        sys.exit(1)
