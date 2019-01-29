import MSGFPlusEngine
import Runners
import DB
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Run MSGF+ Training')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('search_name', help='Name of the MSGF+ Search')
parser.add_argument('mgf_name', help='Name of the MGF')
parser.add_argument('training_name')

parser.add_argument('--memory', type=int, help='The number of megabytes of memory to give the jar file. Default is 3500 megabytes')


args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)

project = MSGFPlusEngine.MSGFPlusEngine(project_folder, ' '.join(sys.argv))



assert(project.verify_row_existence(DB.MSGFPlusSearch.SearchName, args.search_name))
assert(project.verify_row_existence(DB.MGFfile.MGFName, args.mgf_name))
assert(not project.verify_row_existence(DB.MSGFPlusTrainingParams.trainingName, args.training_name))
project.begin_command_session()
msgfplus_training_runner = Runners.MSGFPlusTrainingRunner(os.path.abspath(args.project_folder), project.get_msgfplus_executable_path())

    
if args.memory:
    project.run_training(args.mgf_name, args.search_name, args.training_name, msgfplus_training_runner, args.memory)
else:
    project.run_training(args.mgf_name, args.search_name, args.training_name, msgfplus_training_runner)

project.end_command_session()

