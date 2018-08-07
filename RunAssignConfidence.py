import PostProcessing
import Runners
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Run assign-confidence')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('search_name', help='The name of the tide search to run assign-confidence on')

parser.add_argument('assign_confidence_name', help='The name of the assign-confidence run')
parser.add_argument('--param_file', 'the name of a param file to use')


args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)


project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
crux_exec_path = project.get_crux_executable_path()


project.begin_command_session()

if args.param_file:
    row = project.get_assign_confidence_parameter_file(args.param_file)
    assert(row is not None)
    runner = Runners.AssignConfidenceRunner(crux_exec_path, project.project_path, row)
else:
    runner = Runners.PercolatorRunner(crux_exec_path, project.project_path)

project.assign_confidence(args.search_name, runner, args.assign_confidence_name)
project.end_command_session()

