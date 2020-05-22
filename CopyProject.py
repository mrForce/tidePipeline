import pathlib
import tempfile
import DB
import argparse
import sys
import functools
import os
import shutil
import tarfile


def copy(files_to_really_copy, source, destination):
    paths_to_copy = [pathlib.Path(x) for x in files_to_really_copy]
    if pathlib.Path(source) in paths_to_copy:
        shutil.copy2(source, destination)
    else:
        try:
            os.symlink(source, destination)
            print("Creating symlink for %s to %s" % (source, destination))
        except:
            print("couldn't do symlink. Copying file: %s to %s" % (source, destination))
            shutil.copy2(source, destination)
        

class Ignore:
    def __init__(self, files_to_ignore):
        self.files_to_ignore = files_to_ignore
    def ignore(self, directory, files):
        to_ignore = []
        for name in files:
            if pathlib.Path(os.path.join(directory, name)) in self.files_to_ignore:
                to_ignore.append(name)
        return set(to_ignore)
    

parser = argparse.ArgumentParser(description='Copy a project (only copying over certain NetMHC results for certain alleles)')

parser.add_argument('project_folder', help='The location of the project folder')

parser.add_argument('project_copy', help='Location of the new project')
parser.add_argument('--allele', action='append', help='Copy NetMHC results for this allele')
parser.add_argument('--format', choices=['directory', 'tar', 'targz'], default='directory', help='Is the project a directory, an uncompressed tar file or a .tar.gz file?')

args = parser.parse_args()
project_folder = args.project_folder
files_to_delete = []


#project = Base.Base(project_folder, ' '.join(sys.argv), add_command_row=False)
db_location = None#os.path.join(args.project_copy, 'database.db')
if args.format == 'directory':
    db_location = os.path.join(project_folder, 'database.db')
else:
    assert(tarfile.is_tarfile(project_folder))
    assert(args.format == 'tar' or args.format == 'targz')
    tar_file = tarfile.open(project_folder)
    temporary_file = tempfile.NamedTemporaryFile(delete=False)
    db_file_buffer = tar_file.extractfile('database.db')
    #gives the size in bytes of the database.db file
    db_file_size = tar_file.getmember('database.db').size
    temporary_file.write(db_file_buffer.read())
    db_location = temporary_file.name
    temporary_file.close()
    if not os.path.getsize(db_location) == db_file_size:
        os.remove(db_location)
    assert(os.path.getsize(db_location) == db_file_size)
    files_to_delete.append(db_location)
    
assert(db_location)

db_session = DB.init_session(db_location)
netmhc_rows_query = db_session.query(DB.NetMHC)
netmhc_rows = netmhc_rows_query.all()
#netmhc_rows = project.list_netmhc()

ignore_files = []
print('alleles')
print(args.allele)
ignore_files = set([pathlib.Path(os.path.join(args.project_folder, 'NetMHC', x)) for x in os.listdir(os.path.join(args.project_folder, 'NetMHC'))])
for x in os.listdir(os.path.join(args.project_folder, 'peptides')):
    ignore_files.add(pathlib.Path(os.path.join(args.project_folder, 'peptides', x)))
ignore_files.add(pathlib.Path(os.path.join(args.project_folder, 'database.db.backup')))
keep_files = set()
for row in netmhc_rows:
    hla = row.hla.HLAName
    if args.allele and hla in args.allele:
        keep_files.add(pathlib.Path(os.path.join(args.project_folder, row.PeptideAffinityPath)))
        keep_files.add(pathlib.Path(os.path.join(args.project_folder, row.PeptideRankPath)))
        keep_files.add(pathlib.Path(os.path.join(args.project_folder, row.NetMHCOutputPath)))

print('ignore files')
print(ignore_files)
print('keep files')
print(keep_files)
ignore = Ignore(list(ignore_files - keep_files))
#project.end_command_session()
really_copy_files = [os.path.join(args.project_folder, 'database.db'), os.path.join(args.project_folder, 'config.ini')]

shutil.copytree(args.project_folder, args.project_copy, ignore=ignore.ignore, copy_function=functools.partial(copy, really_copy_files))
with open(os.path.join(args.project_copy, 'copied.txt'), 'w') as f:
    f.write('1')
for x in files_to_delete:
    os.remove(x)
