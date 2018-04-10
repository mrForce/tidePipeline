import tPipeDB
import tPipeProject

import argparse
import sys
import os
from ReportGeneration import *
parser = argparse.ArgumentParser(description='Create a report')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('output', help='The location of the .tex file to store the output in')

parser.add_argument('--assignConfidence', nargs=2, action='append', help='Input the name of the assign-confidence run and the threshold')


args = parser.parse_args()
project_folder = args.project_folder
print('project folder: ' + project_folder)



project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
print('going to begin command session')        
project.begin_command_session(False)
print('starting command session')
assign_confidence_runs = [(tPipeProject.get_assign_confidence(name), threshold) for name,threshold in args.assignConfidence]
report = Report(assign_confidence_runs, project_folder)
report.save_report(args.output)

project.end_command_session(False)

