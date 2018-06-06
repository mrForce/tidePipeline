import tPipeDB
import tPipeProject
import argparse
import sys

import os

parser = argparse.ArgumentParser(description='Filter an assign-confidence, percolator or MSGF+ run by q-value.')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('type', help='Is this an MSGF+, assign-confidence, or percolator run?', choices=['assign_confidence', 'MSGF', 'percolator'])
parser.add_argument('name', help='The name of the MSGF+, assign-confidence or percolator run (depending on type')
parser.add_argument('threshold', help='The q-value threshold', type=float)

parser.add_argument('FilteredSearchResultName')





args = parser.parse_args()

project_folder = args.project_folder


project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
project.begin_command_session()

project.assign_confidence_to_filtered_search_result(args.assign_confidence_name, args.threshold, args.FilteredSearchResultName)
project.end_command_session()
