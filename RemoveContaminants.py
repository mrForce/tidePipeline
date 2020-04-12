import argparse
import Base

parser = argparse.ArgumentParser(description='Pass in a FASTA containing contaminants, a FilteredSearchResult. It will create up to two new FilteredSearchResults: one with no contaminants, and, optionally, one with just contaminants')

parser.add_argument('project_folder', help='The location of the project folder')
parser.add_argument('contaminant_fasta', help='The FASTA containing contaminants')
parser.add_argument('search_result', help='The FilteredSearchResult to remove the contaminants from.')
parser.add_argument('result', help='Name of the FilteredSearchResult that does not have contaminants.')
parser.add_argument('--contaminant_result', help='Name of the FilteredSearchResult that is just the contaminants')




