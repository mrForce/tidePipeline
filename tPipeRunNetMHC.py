import tPipeDB
import tPipeProject

import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Generate a Tide index')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argumen('peptideList', help='Name of the peptidelist to run NetMHC on')
parser.add_argument('HLA', help='Name of the HLA allele to run with NetMHC')
parser.add_argument('rank', help='The rank cutoff', type=float)
parser.add_argument('FilteredNetMHCName', help='The name referring to the set of peptides filtered by NetMHC')


args = parser.parse_args()
assert(float(args.rank) <= 1.0 and float(args.rank) >= 0.0)
project_folder = args.project_folder
print('project folder: ' + project_folder)
project = tPipeProject.Project(project_folder, ' '.join(sys.argv))


project.begin_command_session()
if not project.verify_peptide_List(args.peptideList):
    print('peptide list: ' + args.peptideList + ' does not exist')
    sys.exit()
if not project.verify_hla(args.HLA):
    print('HLA: ' + hla + ' does not exist')
    sys.exit()
if project.verify_filtered_netMHC(args.FilteredNetMHCName):
    print('There is already a FilteredNetMHC entry with that name')
    sys.exit()
    

tPipeProject.run_netmhc(args.peptideList, args.HLA, float(args.rank), args.FilteredNetMHCName)

project.end_command_session()

