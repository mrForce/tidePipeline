import MSGFPlusEngine
import Runners
import DB
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Generate an MSGF+ index')

parser.add_argument('project_folder', help='The location of the project folder')


parser.add_argument('set_type', choices=['FilteredNetMHC', 'PeptideList', 'TargetSet'], help='Are the target peptides comming from a FilteredNetMHC, PeptideList or TargetSet?')
parser.add_argument('set_name', help='The name of the FilteredNetMHC, PeptideList or TargetSet that will be used as targets (depending on the set_type argument)')
parser.add_argument('index_name', help='The name of the index')
parser.add_argument('--memory', type=int, help='The number of megabytes of memory to give the jar file. Default is 3500 megabytes')
parser.add_argument('--contaminantSet', help='The name of a contaminant set to include in the index', nargs='*')
parser.add_argument('--netMHCDecoys', help='The name of a NetMHC which will be used for constructing the decoys', action='append')


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

assert(not project.verify_row_existence(DB.MSGFPlusIndex.MSGFPlusIndexName, args.index_name))
project.begin_command_session()
msgfplus_index_runner = Runners.MSGFPlusIndexRunner(project.get_msgfplus_executable_path())
contaminants = []
if args.contaminantSet:
    contaminants = args.contaminantSet
netmhc_decoys = None
if args.netMHCDecoys:
    netmhc_decoys = []
    for x in args.netMHCDecoys:
        netmhc_row = project.get_netmhc_row(x)
        parsed_location = os.path.abspath(os.path.join(project_folder, netmhc_row.PeptideRankPath))
        netmhc_decoy = (parsed_location, netmhc_row)
        netmhc_decoys.append(netmhc_decoy)
    
if args.memory:
    project.create_index(args.set_type, args.set_name, msgfplus_index_runner, args.index_name, contaminants, args.memory, netmhc_decoys = netmhc_decoys)
else:
    project.create_index(args.set_type, args.set_name, msgfplus_index_runner, args.index_name, contaminants, netmhc_decoys = netmhc_decoys)
project.end_command_session()

