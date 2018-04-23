import tPipeDB
import tPipeProject
import argparse
import sys

import os

parser = argparse.ArgumentParser(description='Create a FilteredSearchResult from Assign Confidence run')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('assign_confidence_name', help='Name of the AssignConfidence run')
parser.add_argument('threshold', help='The q-value threshold', type=float)

parser.add_argument('FilteredSearchResultName')





args = parser.parse_args()

project_folder = args.project_folder


project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
project.begin_command_session()

project.assign_confidence_to_filtered_search_result(args.assign_confidence_name, args.threshold, args.FilteredSearchResultName)            
project.end_command_session()
