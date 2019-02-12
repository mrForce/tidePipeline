import Base
import argparse
import sys
import os
parser = argparse.ArgumentParser(description='Add an MGF file to the project')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('MGFPath', help='The location of the MGF file')

parser.add_argument('MGFName', help='Name of the MGF file (this must be unique')

parser.add_argument('enzyme', type=int, choices=[0, 1, 2, 3, 4, 5, 6, 7, 8], help='What enzyme was used to generate the data? See ScoringParamGen for options')

parser.add_argument('fragmentation', type=int, choices=[0, 1, 2], help='CID, 1: ETD, 2: HCD')
parser.add_argument('instrument', type=int, choices=[0, 1, 2, 3], help='0: Low-res LCQ/LTQ, 1: High-res LTQ, 2: TOF, 3: Q-Exactive')


args = parser.parse_args()

project_folder = args.project_folder


print('project folder: ' + project_folder)


name = args.MGFName
path = args.MGFPath
enzyme = args.enzyme
fragmentation = args.fragmentation
instrument = args.instrument
project = Base.Base(project_folder, ' '.join(sys.argv))
project.begin_command_session()
project.add_mgf_file(path, name, enzyme, fragmentation, instrument)
project.end_command_session()

