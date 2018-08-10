import PostProcessing
import argparse
import sys

parser = argparse.ArgumentParser(description='List Percolator runs')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('--SearchName', help='List only percolator runs that assigned q-values to the given search')

parser.add_argument('--showIterative', help='By default, this doesn\'t show percolator runs that were part of iterative searches. Using this option, it will show percolator runs that were part of iterative searches.', action='store_true')

args = parser.parse_args()

project_folder = args.project_folder



project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
project.begin_command_session()
rows = project.list_percolator(tide_search_name = args.SearchName)
print('id   |   Name   |   Output Path   |   Search Name   ')
for row in rows:
    if (args.showIterative and row.partOfIterativeSearch) or (not row.partOfIterativeSearch):
        percolator_name = row.PercolatorName
        
        percolator_output_path = row.PercolatorOutputPath
        tide_search = row.searchbase
        tide_search_name = 'None'
        if tide_search and tide_search.SearchName:
            tide_search_name = tide_search.SearchName
        print(str(row.idQValue) + '   |   ' + percolator_name + '   |   ' + percolator_output_path + '   |   ' + tide_search_name)

project.end_command_session()
