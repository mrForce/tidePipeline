import MaxQuantEngine
import argparse
import sys

parser = argparse.ArgumentParser(description='List MaxQuant Searches')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('--rawName', help='List only MaxQuant searches that searched against the given RAW file')
args = parser.parse_args()

project_folder = args.project_folder



project = MaxQuantEngine.MaxQuantEngine(project_folder, ' '.join(sys.argv))
project.begin_command_session(False)
searches = project.list_search(raw_name = args.rawName)
print(searches)
project.end_command_session(False)
