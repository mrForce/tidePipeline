import Base
import PostProcessing
import argparse
import sys
import os

parser = argparse.ArgumentParser(description='Export the peptides from a TargetSet, PeptideList, FilteredSearchResult, or FilteredNetMHC')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('CollectionType', help='Is this a TargetSet, PeptideList, FilteredSearchResult or FilteredNetMHC?', choices=['TargetSet', 'PeptideList', 'FilteredSearchResult', 'FilteredNetMHC'])
parser.add_argument('Name', help='The name of the TargetSet, PeptideList FilteredSearchResult or FilteredNetMHC to export')

parser.add_argument('export_location', help='File to put the peptides')

parser.add_argument('--overwrite', help='By default, this script doesn\'t overwrite files. Set this to True if you want to overwrite the output', type=bool, default=False)





args = parser.parse_args()

project_folder = args.project_folder



assert((not os.path.isdir(args.export_location)) or (os.path.commonpath([os.path.abspath(args.export_location), os.devnull]) == os.devnull))


assert(args.overwrite or (not os.path.isfile(args.export_location)))


try:
    with open(args.export_location, 'w') as f:
        pass
except:
    assert(False)
project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
row = None
if args.CollectionType == 'TargetSet':
    row = Base.get_target_set_row(args.Name)
elif args.CollectionType == 'PeptideList':
    row = Base.get_peptide_list_row(args.Name)
elif args.CollectionType == 'FilteredSearchResult':
    row = PostProcessing.get_filtered_search_result_row(args.Name)
elif args.CollectionType == 'FilteredNetMHC':
    row = Base.get_filtered_netmhc_row(args.Name)
assert(row)
peptides = row.get_peptides(project_folder)
with open(args.export_location, 'w') as f:
    for peptide in list(peptides):
        f.write(peptide + '\n')
            
project.end_command_session()
