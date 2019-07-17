import Base
import pathlib
import argparse
import sys
import os
import shutil

def copy(source, destination):
    print('source %s, destination: %s' % (source, destination))
    shutil.copy2(source, destination)


class Ignore:
    def __init__(self, files_to_ignore):
        self.files_to_ignore = files_to_ignore
    def ignore(self, directory, files):
        to_ignore = []
        for name in files:
            if pathlib.Path(os.path.join(directory, name)) in self.files_to_ignore:
                to_ignore.append(name)
        return set(to_ignore)
    

parser = argparse.ArgumentParser(description='Copy a project (only copying over certain NetMHC results for certain alleles)')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('project_copy', help='Location of the new project')
parser.add_argument('--allele', action='append', help='Copy NetMHC results for this allele')

args = parser.parse_args()
project_folder = args.project_folder

project = Base.Base(project_folder, ' '.join(sys.argv), add_command_row=False)

netmhc_rows = project.list_netmhc()
ignore_files = []
print('alleles')
print(args.allele)
ignore_files = set([pathlib.Path(os.path.join(args.project_folder, 'NetMHC', x)) for x in os.listdir(os.path.join(args.project_folder, 'NetMHC'))] + [pathlib.Path(os.path.join(args.project_folder, 'peptides', x)) for x in os.listdir(os.path.join(args.project_folder, 'peptides'))])
keep_files = set()
for row in netmhc_rows:
    hla = row.hla.HLAName
    if hla in args.allele:
        keep_files.add(pathlib.Path(os.path.join(args.project_folder, row.PeptideAffinityPath)))
        keep_files.add(pathlib.Path(os.path.join(args.project_folder, row.PeptideRankPath)))
        keep_files.add(pathlib.Path(os.path.join(args.project_folder, row.NetMHCOutputPath)))

print('ignore files')
print(ignore_files)
print('keep files')
print(keep_files)
input()
ignore = Ignore(list(ignore_files - keep_files))
project.end_command_session()
shutil.copytree(args.project_folder, args.project_copy, ignore=ignore.ignore, copy_function=copy)


