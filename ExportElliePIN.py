import Base
import PostProcessing
import argparse
import sys
import os
import DB
parser = argparse.ArgumentParser(description='Export clean PIN files for search, with NetMHC scores appended to specified alleles.')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('search')
parser.add_argument('positive_fdr')
parser.add_argument('positives_pin')
parser.add_argument('unknown_pin')
parser.add_argument('--allele', help='Name of an allele to run the matches against with NetMHC', action='append')


args = parser.parse_args()

project_folder = args.project_folder



project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
row = project.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName = args.search).first()
print('row')
print(row)            
project.end_command_session()
