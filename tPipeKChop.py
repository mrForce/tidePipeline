import tPipeDB
import tPipeProject
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Generate a list of k-mers from a FASTA file')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)


parser.add_argument('FASTAName', help='Name of the FASTA to use', nargs=1)

parser.add_argument('length', help='length of k-mer', nargs=1)
parser.add_argument('PeptideListName', help='Name of the peptide list', nargs=1)
args = parser.parse_args()
project_folder = args.project_folder[0]
print('project folder: ' + project_folder)
project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
project.begin_command_session()
project.add_peptide_list(args.PeptideListName[0], int(args.length[0]), args.FASTAName[0])
project.end_command_session()

