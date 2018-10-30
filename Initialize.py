import Base
import argparse
import sys
from Errors import *
parser = argparse.ArgumentParser(description='Initialize tPipe Project. This creates a folder, with a sqlite file in it, and subfolders for FASTA, peptides, NetMHC outputs, Tide Indices, MGF files, Tide search results, and Percolator results')

parser.add_argument('project_folder', help='The location of the project folder')
parser.add_argument('config', help='The config file, which is an INI file with three keys in the section EXECUTABLES: the location of the NetMHC executable (netmhc), the location of the crux executable (crux), and the location of the MSGF+ jar file(msgfplus). This is simply copied into the project; if you want to change these values later on, you can manually edit the values within the file')
parser.add_argument('unimodXML', help='The location of a unimod.xml file. This allows interoperability between MSGF+ and Percolator. See: http://www.unimod.org/downloads.html')

args = parser.parse_args()

project_folder = args.project_folder
print('hello')
try:
    Base.Base.createEmptyProject(project_folder, ' '.join(sys.argv), args.config, args.unimodXML)
except ProjectPathAlreadyExistsError as e:
    print('A file or directory already exists at that location. Exiting')
    sys.exit()
except Exception as e:
    sys.exit()
