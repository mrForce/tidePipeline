import Runners
import MSGFPlusEngine

import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Run an MSGFPlus search')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('mgf_name', help='The name of the MGF ')

parser.add_argument('index_name', help='Index name')
parser.add_argument('search_name', help='search name')
parser.add_argument('--modifications_name', help='Name of the modifications file to use. Optional')
parser.add_argument('--memory', help='The amount of memory to give the jar file. Default is 3500 megabytes', type=int)
for k, v in Runners.MSGFPlusSearchRunner.get_search_options().items():
    parser.add_argument(k, **v)


args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)



project = MSGFPlusEngine.MSGFPlusEngine(project_folder, ' '.join(sys.argv))
msgfplus_jar = project.executables['msgfplus']
good_arguments = {}

arguments = vars(args)


for k, v in arguments.items():
    if k and v and k != 'project_folder' and k != 'mgf_name' and k != 'index_name' and k != 'search_name' and k != 'modifications_file':
        k = k.replace('_', '-')
        good_arguments[k] = v
print('going to begin command session')        
project.begin_command_session()
print('starting command session')
search_runner = Runners.MSGFPlusSearchRunner(good_arguments, msgfplus_jar)
print('got MSGF+ search runner')
modifications_name = None
if args.modifications_name:
    modifications_name = args.modifications_name
if args.memory:
    project.run_search(args.mgf_name, args.index_name, modifications_name, search_runner, args.search_name, args.memory)
else:
    project.run_search(args.mgf_name, args.index_name, modifications_name, search_runner, args.search_name)
project.end_command_session()

