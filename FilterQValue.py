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
parser.add_argument('--peptide_q_value', default=False, action='store_true', help='Use peptide level Q-values rather than PSM level Q values')
parser.add_argument('--use_percolator_peptides', default=False, action='store_true', help='If using percolator, turn this option on to use percolator.target.peptides.txt instead of percolator.target.psms.txt')




args = parser.parse_args()

project_folder = args.project_folder


project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
project.begin_command_session()
assert(not project.verify_row_existence(DB.FilteredSearchResult.filteredSearchResultName, args.FilteredSearchResultName))
if args.type  == 'msgf':
    assert(project.verify_row_existence(DB.MSGFPlusSearch.SearchName, args.name))
    project.filter_q_value_msgfplus(args.name, args.threshold, args.FilteredSearchResultName)
else:
    if args.type == 'assign-confidence':
        assert(project.verify_row_existence(DB.AssignConfidence.AssignConfidenceName, args.name))
        project.filter_q_value_assign_confidence(args.name, args.threshold, args.FilteredSearchResultName)
    elif args.type == 'percolator':
        assert(project.verify_row_existence(DB.Percolator.PercolatorName, args.name))
        project.filter_q_value_percolator(args.name, args.threshold, args.FilteredSearchResultName, use_percolator_peptides = args.use_percolator_peptides)
project.end_command_session()
