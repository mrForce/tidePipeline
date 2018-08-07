import Runners
import TideEngine

import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Run a tide search')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('mgf_name', help='The name of the MGF ')

parser.add_argument('index_name', help='Index name')
parser.add_argument('search_name', help='search name')
parser.add_argument('--param_file', help='Location of param file')



args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)



project = TideEngine.TideEngine(project_folder, ' '.join(sys.argv))
crux_exec_path = project.get_crux_executable_path()


print('going to begin command session')        
project.begin_command_session()
print('starting command session')
if args.param_file:
    row = project.get_tide_search_parameter_file(args.param_file)
    assert(row is not None)
    tide_search_runner = Runners.TideSearchRunner(crux_exec_path, project.project_path, row)
else:
    tide_search_runner = Runners.TideSearchRunner(crux_exec_path, project.project_path)
print('got tide search runner')
project.run_search(args.mgf_name, args.index_name, tide_search_runner, args.search_name)
project.end_command_session()

