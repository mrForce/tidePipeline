import TideEngine
import Runners

import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Generate a Tide index')

parser.add_argument('project_folder', help='The location of the project folder')


parser.add_argument('set_type', choices=['FilteredNetMHC', 'PeptideList', 'TargetSet'], help='Are the target peptides comming from a FilteredNetMHC, PeptideList or TargetSet?')
parser.add_argument('set_name', help='The name of the FilteredNetMHC, PeptideList or TargetSet that will be used as targets (depending on the set_type argument)')
parser.add_argument('index_name', help='The name of the index')
parser.add_argument('--param_file', help='The name of a param file to use')




for k, v in Runners.TideIndexRunner.get_tide_index_options().items():
    parser.add_argument(k, **v)


args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)

project = TideEngine.TideEngine(project_folder, ' '.join(sys.argv))
crux_exec_path = project.get_crux_executable_path()
arguments = vars(args)
good_arguments = {}

arguments = vars(args)


for k, v in arguments.items():
    if k and v and k != 'set_type' and k != 'set_name' and k != 'project_folder' and k != 'index_name':
        k = k.replace('_', '-')
        good_arguments[k] = v
if args.set_type == 'FilteredNetMHC':
    assert(project.verify_filtered_netMHC(args.set_name))
elif args.set_type == 'PeptideList':
    assert(project.verify_peptide_list(args.set_name))
elif args.set_type == 'TargetSet':
    assert(project.verify_target_set(args.set_name))
            
project.begin_command_session()
if args.param_file:
    row = project.get_tide_index_parameter_file(args.param_file)
    assert(row is not None)
    tide_index_runner = Runners.TideIndexRunner(good_arguments, crux_exec_path, project.project_path, row)
else:
    tide_index_runner = Runners.TideIndexRunner(good_arguments, crux_exec_path, project.project_path)
project.create_index(args.set_type, args.set_name, tide_index_runner, args.index_name)
project.end_command_session()

