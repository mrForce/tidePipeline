import tPipeDB
import tPipeProject

import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Generate a Tide index')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)

parser.add_argument('index_name', help='The name of the index')

parser.add_argument('--peptideList', help='Name of a PeptideList to include in the index', action='append')
parser.add_argument('--netMHCFilter', help='Follow this with a PeptideList name, HLA, and rank cutoff', nargs=3, action='append')

for k, v in tPipeProject.TideIndexRunner.get_tide_index_options().items():
    parser.add_argument(k, **v)


args = parser.parse_args()
project_folder = args.project_folder[0]
print('project folder: ' + project_folder)
if len(args.peptideList) == 0 and len(args.netMHCFilter) == 0:
    print('you need to specify at least one netMHCFilter or peptideList')
else:
    project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
    project.begin_command_session()
    tide_index_runner = tPipeProject.TideIndexRunner(vars(args))
    project.create_tide_index(args.peptideList, args.netMHCFilter, tide_index_runner, args.index_name)
    project.end_command_session()

