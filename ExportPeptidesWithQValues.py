import Base
import PostProcessing
import argparse
import sys
import os
import CSV

parser = argparse.ArgumentParser(description='Export the peptides and their Q-Values from Percolator')

parser.add_argument('project_folder', help='The location of the project folder')


parser.add_argument('Name', help='The name of the Percolator to export.')

parser.add_argument('export_location', help='File to put the peptides and q-values (as tab seperated values)')



args = parser.parse_args()

project_folder = args.project_folder



assert(not os.path.isfile(args.export_location))



project = PostProcessing.PostProcessing(project_folder, ' '.join(sys.argv))
project.begin_command_session()
q_values = project.get_percolator_peptide_q_values(args.Name)
with open(args.export_location, 'w') as tsv_output:
    fieldnames = ['Peptide', 'Q-Value']
    writer = csv.DictWriter(tsv_output, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    for peptide,q in q_values:
        writer.writerow({'Peptide': peptide, 'Q-Value': q})
    

project.end_command_session()
