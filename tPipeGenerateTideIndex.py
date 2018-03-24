import tPipeDB
import tPipeProject
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Generate a tide index from Peptide Lists, and running Peptide Lists through NetMHC with a rank cutoff')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

parser.add_argument('index_name', help='The name of the tide index', nargs=1)
parser.add_argument('--PeptideList', help='The name of a Peptide List', nargs=1, action='append')
parser.add_argument('--NetMHCFilter', help='Pass it three arguments: the HLA name, peptide list name, and rank cutoff', nargs=3, action='append')
args = parser.parse_args()
project_folder = args.project_folder[0]
print('project folder: ' + project_folder)
print('index name')
print(args.index_name)
print('peptide lists')
print(args.PeptideList)
print('NetMHC filters')
print(args.NetMHCFilter)

project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
project.begin_command_session()

project.end_command_session()
