import MSGFPlusEngine
import Runners

import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Generate an MSGF+ index')

parser.add_argument('project_folder', help='The location of the project folder')


parser.add_argument('set_type', choices=['FilteredNetMHC', 'PeptideList', 'TargetSet'], help='Are the target peptides comming from a FilteredNetMHC, PeptideList or TargetSet?')
parser.add_argument('set_name', help='The name of the FilteredNetMHC, PeptideList or TargetSet that will be used as targets (depending on the set_type argument)')
parser.add_argument('index_name', help='The name of the index')
parser.add_argument('--memory', type=int, help='The number of megabytes of memory to give the jar file. Default is 3500 megabytes')




args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)

project = MSGFPlusEngine.MSGFPlusEngine(project_folder, ' '.join(sys.argv))



if args.set_type == 'FilteredNetMHC':
    assert(project.verify_filtered_netMHC(args.set_name))
elif args.set_type == 'PeptideList':
    assert(project.verify_peptide_list(args.set_name))
elif args.set_type == 'TargetSet':
    assert(project.verify_target_set(args.set_name))
            
project.begin_command_session()
msgfplus_index_runner = Runners.MSGFPlusIndexRunner(project.get_msgfplus_executable_path())
if args.memory:
    project.create_index(args.set_type, args.set_name, msgfplus_index_runner, args.index_name, memory)
else:
    project.create_index(args.set_type, args.set_name, msgfplus_index_runner, args.index_name)
project.end_command_session()

