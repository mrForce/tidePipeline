import Base
import Runners
import DB
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Take a FASTA file, and create a new FASTA file with the old one, plus all of the proteins shuffled')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('old_fasta_name')
parser.add_argument('new_fasta_name')


args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)

project = Base.Base(project_folder, ' '.join(sys.argv))

project.begin_command_session()
fasta_row = project.get_fasta_row(args.old_fasta_name)
project.shuffle_fasta(fasta_row, args.new_fasta_name)
project.end_command_session()

