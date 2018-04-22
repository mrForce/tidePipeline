import tPipeDB
import tPipeProject

import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Create a TargetSet from FilteredNetMHCs and PeptideLists')

parser.add_argument('project_folder', help='The location of the project folder')



parser.add_argument('--PeptideList', help='Name of a PeptideList to include in the TargetSet', action='append')
parser.add_argument('--FilteredNetMHC', help='Name of a FilteredNetMHC to include in the TargetSet', action='append')

parser.add_argument('TargetSetName,' help='Name of the TargetSet')

args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)
if args.peptideList is None and args.netMHCFilter is None:
    print('you need to specify at least one FilteredNetMHC or PeptideList')
else:
    project = tPipeProject.Project(project_folder, ' '.join(sys.argv))            
    project.begin_command_session()
    project.add_targetset(args.FilteredNetMHC, args.PeptideList, args.TargetSetName)
    project.end_command_session()

