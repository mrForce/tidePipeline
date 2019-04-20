import Base

import argparse
import sys
import os
import shutil

parser = argparse.ArgumentParser(description='Copy a project (only copying over certain NetMHC results for certain alleles)')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('project_copy', help='Location of the new project')
parser.add_argument('--allele', action='append', help='Copy NetMHC results for this allele')

args = parser.parse_args()
project_folder = args.project_folder

project = Base.Base(project_folder, ' '.join(sys.argv))

netmhc_rows = project.list_netmhc()
ignore_files = []
print('alleles')
print(args.allele)
for row in netmhc_rows:
    hla = row.hla.HLAName
    if hla not in args.allele:
        ignore_files.append(row.PeptideAffinityPath)
        ignore_files.append(row.PeptideRankPath)
        ignore_files.append(row.NetMHCOutputPath)

print('ignore files')
print(ignore_files)

shutil.copytree(args.project_folder, args.project_copy, ignore=shutil.ignore_patterns(*ignore_files))
project.end_command_session()

