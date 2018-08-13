import PostProcessing
import argparse
import sys
import DB
import os

parser = argparse.ArgumentParser(description='Filter an assign-confidence, percolator or MSGF+ run by q-value.')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('type', help='Is this an MSGF+, assign-confidence, or percolator run?', choices=['assign-confidence', 'msgf', 'percolator'])
parser.add_argument('name', help='The name of the MSGF+, assign-confidence or percolator run (depending on type)')
parser.add_argument('threshold', help='The q-value threshold', type=float)

parser.add_argument('FilteredSearchResultName')




args = parser.parse_args()

project_folder = args.project_folder


project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
project.begin_command_session()
assert(not project.verify_row_existence(DB.FilteredSearchResult.filteredSearchResultName, args.FilteredSearchResultName))
assert(project.verify_search(args.type, args.name))
if args.type  == 'msgf':
    project.filter_q_value_msgfplus(args.name, args.threshold, args.FilteredSearchResultName)
else:
    if args.type == 'assign-confidence':
        project.filter_q_value_assign_confidence(args.name, args.threshold, args.FilteredSearchResultName)
    elif args.type == 'percolator':
        project.filter_q_value_percolator(args.name, args.threshold, args.FilteredSearchResultName)
project.end_command_session()
