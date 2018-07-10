import PostProcessing
import Runners
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Run percolator')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('search_name', help='The name of the tide search to percolator on')

parser.add_argument('percolator_name', help='The name of the percolator run')


parser.add_argument('--param_file', help='The path to a param file')


args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)


project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
crux_exec_path = project.get_crux_executable_path()
arguments = vars(args)
project.begin_command_session()
percolator_runner = None
if args.param_file:
    percolator_runner = Runners.PercolatorRunner(crux_exec_path, args.param_file)
else:
    percolator_runner = Runners.PercolatorRunner(crux_exec_path)
percolator_name = args.percolator_name
project.percolator(args.search_name, percolator_runner, percolator_name)
project.end_command_session()

