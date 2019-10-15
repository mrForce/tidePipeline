import Base
from shutil import copyfile
import PostProcessing
import argparse
import sys
import os

parser = argparse.ArgumentParser(description='For a given allele and length, get the file containing the NetMHC scores from the NetMHC directory.')

parser.add_argument('project_folder', help='The location of the project folder')
parser.add_argument('allele', type=str)
parser.add_argument('length', type=int)
parser.add_argument('export_location', help='File to put the peptides')



args = parser.parse_args()


project_folder = args.project_folder

project = Base.Base(project_folder, ' '.join(sys.argv), add_command_row=False)
project.begin_command_session()

netmhc_rows = project.list_netmhc()

for row in netmhc_rows:
    hla = row.hla.HLAName
    if hla == args.allele and length == row.length():
        copyfile(os.path.join(project_folder, row.PeptideAffinityPath), args.export_location)
        break
