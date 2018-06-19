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


for k, v in Runners.TideSearchRunner.get_tide_search_options().items():
    parser.add_argument(k, **v)


args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)



project = TideEngine.TideEngine(project_folder, ' '.join(sys.argv))
arguments = vars(args)
good_arguments = {}

arguments = vars(args)


for k, v in arguments.items():
    if k and v and k != 'project_folder' and k != 'mgf_name' and k != 'index_name' and k != 'search_name':
        k = k.replace('_', '-')
        good_arguments[k] = v
print('going to begin command session')        
project.begin_command_session()
print('starting command session')
tide_search_runner = Runners.TideSearchRunner(good_arguments)
print('got tide search runner')
project.run_search(args.mgf_name, args.index_name, tide_search_runner, args.search_name, good_arguments)
project.end_command_session()

