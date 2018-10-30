import PostProcessing
import argparse
import sys

parser = argparse.ArgumentParser(description='List Filtered Search Results')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)
parser.add_argument('--showIterative', help='By default, this doesn\'t show filtered search results that were part of iterative searches. Using this option, it will show filtered search results that were part of iterative searches.', action='store_true')
args = parser.parse_args()
project_folder = args.project_folder[0]
project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
project.begin_command_session()
results_table = project.list_filtered_search_results(args.showIterative)
print(results_table)
project.end_command_session()
