import Runners
import MaxQuantEngine

import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Run a MaxQuant search')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('raw_name', help='The name of the RAW')
parser.add_argument('param_file_name')
parser.add_argument('fdr', help='The FDR', type=float)
parser.add_argument('set_type', choices=['FilteredNetMHC', 'PeptideList', 'TargetSet'], help='Are the target peptides comming from a FilteredNetMHC, PeptideList or TargetSet?')
parser.add_argument('set_name', help='The name of the FilteredNetMHC, PeptideList or TargetSet that will be used as targets (depending on the set_type argument)')
parser.add_argument('search_name', help='search name')




args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)



project = MaxQuantEngine.MaxQuantEngine(project_folder, ' '.join(sys.argv))
project.begin_command_session()
print('starting command session')
maxquant_search_runner = Runners.MaxQuantSearchRunner(project.executables['maxquant'])
print('got maxquant search runner')
project.run_search(args.raw_name, args.param_file_name, maxquant_search_runner, args.search_name, args.set_type, args.set_name, args.fdr)
project.end_command_session()

