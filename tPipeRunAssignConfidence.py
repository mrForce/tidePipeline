import tPipeDB
import tPipeProject

import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Run assign-confidence')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('search_name', help='The name of the tide search to run assign-confidence on')

parser.add_argument('assign_confidence_name', help='The name of the assign-confidence run')


for k, v in tPipeProject.AssignConfidenceRunner.get_assign_confidence_options().items():
    parser.add_argument(k, **v)


args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)


project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
arguments = vars(args)
good_arguments = {}

arguments = vars(args)


for k, v in arguments.items():
    if k and v and k != 'search_name' and k != 'assign_confidence_name' and k != 'project_folder':
        k = k.replace('_', '-')
        good_arguments[k] = v

project.begin_command_session()
assign_confidence_runner = tPipeProject.AssignConfidenceRunner(good_arguments)
project.assign_confidence(args.search_name, assign_confidence_runner, args.assign_confidence_name)
project.end_command_session()

