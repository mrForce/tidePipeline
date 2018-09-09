import Base
import argparse
import sys
parser = argparse.ArgumentParser(description='Import a PeptideList')
parser.add_argument('project_folder')
parser.add_argument('location')
parser.add_argument('FASTA')
parser.add_argument('PeptideListName')

args = parser.parse_args()
project_folder = args.project_folder
location = args.location
fasta = args.FASTA
name = args.PeptideListName
project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
project.import_peptide_list(name, fasta, location)
project.end_command_session()
