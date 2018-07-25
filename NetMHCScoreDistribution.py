import PostProcessing

import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Get score distribution of peptides in a TargetSet, PeptideList, FilteredSearchResult, TideIterativeSearch, MSGFPlusIterativeSearch, MaxQuantSearch, or FilteredNetMHC')


parser.add_argument('project_folder', help='The location of the project folder')
parser.add_argument('CollectionType', help='Is this a TargetSet, PeptideList, FilteredSearchResult, Tide Iterative Search, MaxQuantSearch or FilteredNetMHC?', choices=['TargetSet', 'PeptideList', 'FilteredSearchResult', 'FilteredNetMHC', 'MaxQuantSearch', 'TideIterativeSearch', 'MSGFPlusIterativeSearch'])
parser.add_argument('CollectionName', help='Name of the collection to score')
parser.add_argument('--mhc', help='Name of the MHC allele to run with NetMHC', action='append')
parser.add_argument('output_location', help='File to put the scores')

parser.add_argument('--overwrite', help='By default, this script doesn\'t overwrite files. Set this to True if you want to overwrite the output', type=bool, default=False)

parser.add_argument('--netMHCPan', action='store_true', help='Use netMHCPan')

args = parser.parse_args()
assert(len(args.mhc) > 0)

assert((not os.path.isdir(args.output_location)) or (os.path.commonpath([os.path.abspath(args.output_location), os.devnull]) == os.devnull))


assert(args.overwrite or (not os.path.isfile(args.output_location)))


try:
    with open(args.output_location, 'w') as f:
        pass
except:
    assert(False)


project_folder = args.project_folder
print('project folder: ' + project_folder)
project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))


project.begin_command_session()
for mhc in args.mhc:
    if not project.verify_hla(mhc):
        print('MHC: ' + mhc + ' does not exist')
        sys.exit()


scores = project.netmhc_rank_distribution(args.CollectionType, args.CollectionName, args.mhc, args.netMHCPan)

with open(args.output_location, 'w') as f:
    f.write(str(', '.join(args.mhc)) + '\n')
    for peptide, score_list in scores.items():
        f.write(peptide + ', ' + ', '.join(score_list) + '\n')


        
project.end_command_session()

