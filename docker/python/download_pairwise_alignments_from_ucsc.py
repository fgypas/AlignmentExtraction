#!/usr/bin/env python

__version__ = "0.1"
__author__ = "Foivos Gypas"
__contact__ = "foivos.gypas@unibas.ch"
__doc__ = "Download pairwise alignments from ucsc"

# _____________________________________________________________________________
# -----------------------------------------------------------------------------
# import needed (external) modules
# -----------------------------------------------------------------------------

import sys
import os
import wget
from argparse import ArgumentParser, RawTextHelpFormatter

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
        "--organism",
        dest="organism",
        help="Reference organism (e.g. hg38, hg19, mm10)",
        required=True,
        metavar="FILE"
    )

    parser.add_argument(
        "--organism_link",
        dest="organism_link",
        help="Link to organism",
        required=True
    )

    parser.add_argument(
        "--organism_to_download",
        dest="organism_to_download",
        help="Name of pairwise alignment organism, without assembly version",
        required=True
    )

    parser.add_argument(
        "--assemblies",
        dest="assemblies",
        help="File with list of organisms with their newest assembly number",
        required=True
    )

    parser.add_argument(
        "--out",
        dest="out",
        help="Output directory",
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

    # Get the needed assembly from file
    try:
        with open(options.assemblies) as f:
            assemblies = f.read().split(',')
            org_version = [x for x in assemblies if options.organism_to_download.lower() in x.lower()]
            if not org_version:
                print("Organism to download not in provided assembly list!")
                sys.exit(1)
            elif len(org_version) > 1:
                print("Multiple versions for organism to download given in assembly list!")
                sys.exit(1)
            org_version = org_version[0]
    except:
        sys.stderr.write("Couldn't load assemblies file.")

    start = options.organism_link
    f_s_l = org_version
    f_s = f_s_l[0].upper() + f_s_l[1:]
    output_dir = os.path.join(options.out, options.organism + "_to_" + options.organism_to_download)
    out_file_name = options.organism + "." + options.organism_to_download + ".net.axt.gz"
    remote_file_name = options.organism + "." + f_s_l + ".net.axt.gz"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    download_link = os.path.join(start + f_s, remote_file_name)
    try:
        if options.verbose:
            sys.stdout.write("Downloading " + download_link + os.linesep)
        wget.download(download_link, os.path.join(output_dir, out_file_name))
    except:
        sys.stderr.write("Could not download " + download_link + os.linesep)

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
