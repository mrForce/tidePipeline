import Base
import argparse
import sys
import pprint
import ReportGeneration
parser = argparse.ArgumentParser(description='Create a report about a assign confidence runs')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('q_value', help='q-value threshold', type=float)

parser.add_argument('AssignConfidenceNames', help='Names of the assign confidence entries', nargs='+')

parser.add_argument('output_location', help='where to save the report')

args = parser.parse_args()

project_folder = args.project_folder



project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
assign_confidence_runs = []
for name in args.AssignConfidenceNames:
    row = project.get_assign_confidence(name)
    assert(row)
    assign_confidence_runs.append((row, args.q_value))

report = ReportGeneration.Report(assign_confidence_runs, project.project_path)

project.end_command_session()
report.save_report(args.output_location)
