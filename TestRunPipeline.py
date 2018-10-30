import Pipeline
import argparse

parser = argparse.ArgumentParser(description='Test run a pipeline')

parser.add_argument('project_folder', help='The location of the project folder')
parser.add_argument('ini_file', help='location of the ini file')
parser.add_argument('image_location', help='location of the image to output')
args = parser.parse_args()

project_folder = args.project_folder
ini_file = args.ini_file
image = args.image_location

Pipeline.run_pipeline(ini_file, project_folder, image, True)
