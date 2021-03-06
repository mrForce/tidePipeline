import Base
import argparse
import sys

parser = argparse.ArgumentParser(description='This is for listing the history of commands')

parser.add_argument('project_folder', help='The location of the project folder', nargs=1)


args = parser.parse_args()

project_folder = args.project_folder[0]

print('project folder: ' + project_folder)


project = Base.Base(project_folder, ' '.join(sys.argv))

for command in project.get_commands():
    print(command)

