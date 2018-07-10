import PostProcessing
import argparse
import sys

parser = argparse.ArgumentParser(description='List Assign Confidence runs')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('--SearchName', help='List only assign-confidence runs that assigned confidences to the given search')
parser.add_argument('--estimationMethod', help='List only assign-confidence runs that used the given estimation method', choices=['min-max', 'tdc', 'peptide-level'])
args = parser.parse_args()

project_folder = args.project_folder



project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
project.begin_command_session()
rows = project.list_assign_confidence(tide_search_name = args.SearchName, estimation_method = args.estimationMethod)
print('id   |   Name   |   Output Path   |   Search Name   |   estimation method   |   score type   |   sidak')
for row in rows:
    assign_confidence_name = row.AssignConfidenceName
    assign_confidence_output_path = row.AssignConfidenceOutputPath
    tide_search = row.search
    tide_search_name = 'None'
    if tide_search and tide_search.SearchName:
        tide_search_name = tide_search.SearchName
    #tdc is the default
    estimation_method = 'tdc'
    if row.estimation_method:
        estimation_method = row.estimation_method
    score_type = '<empty>'
    if row.score:
        score_type = row.score
    sidak = 'False'
    if row.sidak:
        sidak = row.sidak
    print(str(row.idQValue) + '   |   ' + assign_confidence_name + '   |   ' + assign_confidence_output_path + '   |   ' + tide_search_name + '   |   ' + estimation_method + '   |   ' + score_type + '   |   ' + sidak)
project.end_command_session()
