
import Base
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Generate a list of k-mers from a FASTA file')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)


parser.add_argument('FASTAName', help='Name of the FASTA to use', nargs=1)

parser.add_argument('length', help='length of k-mer', nargs=1)
parser.add_argument('PeptideListName', help='Name of the peptide list', nargs=1)
parser.add_argument('--context', help='Number of amino acids of context to put in the FASTA header', default=0, type=int)
args = parser.parse_args()
project_folder = args.project_folder[0]
print('project folder: ' + project_folder)
project = Base.Base(project_folder, ' '.join(sys.argv))
context = args.context
project.begin_command_session()
project.add_peptide_list(args.PeptideListName[0], int(args.length[0]), args.FASTAName[0], context = context)
project.end_command_session()

