import tPipeDB
import tPipeProject
import argparse
import sys
from ReportGeneration import *
import os

parser = argparse.ArgumentParser(description='Export the peptides from an AssignConfidence run to a file -- also prints out the number of unique peptides')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('assign_confidence_name', help='Name of the AssignConfidence run')
parser.add_argument('threshold', help='The q-value threshold', type=float)

parser.add_argument('export_location', help='File to put the peptide list')

parser.add_argument('--overwrite', help='By default, this script doesn\'t overwrite files. Set this to True if you want to overwrite the output', type=bool, default=False)

parser.add_argument('--includePeptideSource', help='include this if you want to show which NetMHC runs or PeptideList each peptide comes from.', type=bool, default=False)





args = parser.parse_args()

project_folder = args.project_folder



assert((not os.path.isdir(args.export_location)) or (os.path.commonpath([os.path.abspath(args.export_location), os.devnull]) == os.devnull))


assert(args.overwrite or (not os.path.isfile(args.export_location)))

assert(args.threshold <= 1.0 and args.threshold > 0.0)

try:
    with open(args.export_location, 'w') as f:
        pass
except:
    assert(False)
project = tPipeProject.Project(project_folder, ' '.join(sys.argv))
project.begin_command_session()

row = project.get_assign_confidence(args.assign_confidence_name)
if row:
    q_val_column = 'tdc q-value'
    if row.estimation_method and len(row.estimation_method) > 0:
        q_val_column = row.estimation_method + ' q-value'
    handler = AssignConfidenceHandler(row, q_val_column, args.threshold, project_folder)
    peptides = handler.getPeptides()
    print('Num unique peptides: ' + str(len(peptides)))
    with open(args.export_location, 'w') as f:
        for peptide in list(peptides):
            f.write(peptide + '\n')
            
project.end_command_session()
