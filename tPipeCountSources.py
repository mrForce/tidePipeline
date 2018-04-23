import tPipeDB
import tPipeProject
import argparse
import sys
import pprint
parser = argparse.ArgumentParser(description='List Assign Confidence runs')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('AssignConfidenceName', help='Name of the assign confidence entry')

parser.add_argument('q_value', help='q-value threshold', type=float)

args = parser.parse_args()

project_folder = args.project_folder



project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
project.begin_command_session()
pprint.pprint(project.count_sources(args.AssignConfidenceName, args.q_value))
project.end_command_session()
