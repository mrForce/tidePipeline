import tPipeDB
import tPipeProject
import argparse
import sys

parser = argparse.ArgumentParser(description='List Assign Confidence runs')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('--tideSearchName', help='List only assign-confidence runs that assigned confidences to the given tide search')
parser.add_argument('--estimationMethod', help='List only assign-confidence runs that used the given estimation method', choices=['min-max', 'tdc', 'peptide-level'])
args = parser.parse_args()

project_folder = args.project_folder



project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
project.begin_command_session()
rows = project.list_assign_confidence(tide_search_name = args.tideSearchName, estimation_method = args.estimationMethod)
print('id   |   Name   |   Output Path   |   Tide Search Name   |   estimation method   |   score type   |   sidak')
for row in rows:
    print(str(row.idAssignConfidence) + '   |   ' + row.AssignConfidenceName + '   |   ' + row.AssignConfidenceOutputPath + '   |   ' + row.tideSearch.TideSearchName + '   |   ' + row.estimation_method + '   |   ' + row.score + '   |   ' + row.sidak)
project.end_command_session()
