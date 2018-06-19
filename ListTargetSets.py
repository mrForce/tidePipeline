import Base
import argparse
import sys

parser = argparse.ArgumentParser(description='List TargetSets')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)
args = parser.parse_args()
project_folder = args.project_folder[0]
project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
print(project.list_targetsets())
project.end_command_session()
