import Base

import argparse
import sys
import os

class NameCreator:
    def __init__(self, start_string):
        self.start_string = start_string
        self.version = 0
    def increase_version(self):
        self.version += 1
    def __str__(self):
        if self.version == 0:
            return self.start_string
        else:
            return self.start_string + '_' + str(self.version)
parser = argparse.ArgumentParser(description='Filter a PeptideList by NetMHC rank.')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('peptideList', help='Name of the peptidelist to run NetMHC on')
parser.add_argument('HLA', help='Name of the HLA allele to run with NetMHC')
parser.add_argument('--rank', help='The rank cutoff', type=float)


parser.add_argument('--netMHCPan', action='store_true', help='Use netMHCPan')

args = parser.parse_args()
if args.rank:
    assert(args.rank <= 100.0 and args.rank > 0)
project_folder = args.project_folder
print('project folder: ' + project_folder)
project = Base.Base(project_folder, ' '.join(sys.argv))

netmhc_name = args.peptideList + '_' + args.HLA

project.begin_command_session()
if not project.verify_peptide_list(args.peptideList):
    print('peptide list: ' + args.peptideList + ' does not exist')
    sys.exit()
if not project.verify_hla(args.HLA):
    print('HLA: ' + args.HLA + ' does not exist')
    sys.exit()
filtered_netmhc_name = False
if args.rank:
    filtered_netmhc_name = netmhc_name + '_' + args.rank
    name_creator = NameCreator(filtered_netmhc_name)
    while project.verify_filtered_netMHC(str(name_creator)):
        name_creator.increase_version()
    filtered_netmhc_name = str(name_creator)
print(args.peptideList)
print(args.HLA)
print(args.rank)
if filtered_netmhc_name:
    print('filtered name: ' + str(name_creator))

#project.run_netmhc(args.peptideList, args.HLA, args.rank, netmhc_name, str(name_creator), args.netMHCPan)
"""
Note: if filtered_netmhc_name is False, then it doesn't generate a FilteredNetMHC.
"""
project.run_netmhc(args.peptideList, args.HLA, args.rank, netmhc_name, filtered_netmhc_name, args.netMHCPan)

project.end_command_session()

