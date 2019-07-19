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
parser.add_argument('rank', help='The rank cutoff', type=str)


parser.add_argument('--netMHCPan', action='store_true', help='Use netMHCPan')

args = parser.parse_args()
assert(float(args.rank) <= 100.0 and float(args.rank) >= 0.0)
project_folder = args.project_folder
print('project folder: ' + project_folder)
project = Base.Base(project_folder, ' '.join(sys.argv))

netmhc_name = args.peptideList + '_' + args.HLA
filtered_netmhc_name = netmhc_name + '_' + args.rank
project.begin_command_session()
if not project.verify_peptide_list(args.peptideList):
    print('peptide list: ' + args.peptideList + ' does not exist')
    sys.exit()
if not project.verify_hla(args.HLA):
    print('HLA: ' + args.HLA + ' does not exist')
    sys.exit()
name_creator = NameCreator(filtered_netmhc_name)
while project.verify_filtered_netMHC(str(name_creator)):
    name_creator.increase_version()

print(args.peptideList)
print(args.HLA)
print(args.rank)
print('filtered name: ' + str(name_creator))

#project.run_netmhc(args.peptideList, args.HLA, args.rank, netmhc_name, str(name_creator), args.netMHCPan)
"""
Changed this on Saturday April 20th, so that we wouldn't do the ran cutoff stuff
"""
project.run_netmhc(args.peptideList, args.HLA, args.rank, netmhc_name, False, args.netMHCPan)

project.end_command_session()

