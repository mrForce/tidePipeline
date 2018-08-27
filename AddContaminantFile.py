import Base
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Add a FASTA or peptide file of contaminants to the project. ')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

parser.add_argument('Format', choices=['FASTA', 'peptides'], help='Give it the format. It can either be FASTA or peptides -- peptides is where the peptides are seperated by a newline.')

parser.add_argument('Path', help='Path to the FASTA file of contaminants')

parser.add_argument('Name', help='Name of the contaminants')

parser.add_argument('lengths', help='peptide lengths to chop the contaminants into. If you don\'t supply anything, no chopping will occur', nargs='*', type=int)

args = parser.parse_args()

project_folder = args.project_folder[0]


print('project folder: ' + project_folder)


name = args.Name
path = args.Path
lengths = args.lengths
print('name: ' + name)

project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
project.add_contaminant_file(path, name, lengths, args.Format)
project.db_session.commit()
project.end_command_session()

