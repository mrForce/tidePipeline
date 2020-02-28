import Base
import PostProcessing
import argparse
import sys
import os
import csv

parser = argparse.ArgumentParser(description='Export the PSMs and their Q-Values from Percolator')

parser.add_argument('project_folder', help='The location of the project folder')


parser.add_argument('Name', help='The name of the Percolator to export.')

parser.add_argument('export_location', help='File to put the scans, peptides and q-values (as tab seperated values)')



args = parser.parse_args()

project_folder = args.project_folder



#assert(not os.path.isfile(args.export_location))



project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
project.begin_command_session()
q_values = sorted(project.get_percolator_psms(args.Name), key=lambda x: x[2])

with open(args.export_location, 'w') as tsv_output:
    fieldnames = ['Scan', 'Peptide', 'Q-Value']
    writer = csv.DictWriter(tsv_output, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    for scan,peptide,q in q_values:
        writer.writerow({'Scan': scan, 'Peptide': peptide, 'Q-Value': q})
    

project.end_command_session()
