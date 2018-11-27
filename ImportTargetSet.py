import Base
import argparse
import sys
parser = argparse.ArgumentParser(description='Import a file containing peptides as a TargetSet')
parser.add_argument('project_folder')
parser.add_argument('peptides_location')
parser.add_argument('targetset_name')

args = parser.parse_args()
project_folder = args.project_folder
location = args.peptides_location


name = args.targetset_name
project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
project.import_targetset(location, name)
project.end_command_session()
