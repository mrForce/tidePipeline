from Bio import SeqIO
import re
import subprocess
import os
import glob
import re
import shutil
def extract_peptides(fasta_path, length):
    peptides = set()
    with open(fasta_path, 'rU') as handle:
        for record in SeqIO.parse(handle, 'fasta'):
            sequence = record.seq
            if len(sequence) >= length:
                for i in range(0, len(sequence) - length + 1):
                    peptide = sequence[i:(i + length)]
                    peptides.add(str(peptide))
    return peptides

def write_peptides(file_path, peptide_set):
    peptide_list = list(peptide_set)
    with open(file_path, 'w') as f:
        for x in peptide_list:
            f.write(x + '\n')

def find_unique_name(existing_names, proposed_name, regex, extension_index = None):
    if proposed_name in existing_names:
        max_version = 0
        for existing_name in existing_names:
            version_string_match = regex.match(existing_name)
            if version_string_match is not None:
                version_string = version_string_match.group('version')
                if version_string is not None and len(version_string) > 0 and int(version_string) > max_version:
                    max_version = int(version_string)
        if extension_index is None:
            new_name = proposed_name + '-' + str(max_version + 1)
        else:
            new_name = proposed_name[0:extension_index] + '-' + str(max_version + 1) + proposed_name[extension_index::]

        return new_name
    else:
        return proposed_name
                    
    
def copy_file_unique_basename(filepath, destination_folder, file_extension = False):
    #returns the new basename
    if file_extension:
        existing_files = glob.glob(os.path.join(destination_folder, '*.' + file_extension))
    else:
        existing_files = glob.glob(os.path.join(destination_folder, '*'))
    existing_basenames = [os.path.basename(file_name) for file_name in existing_files]
    file_basename = os.path.basename(filepath)
    extension_index = -1
    if file_basename in existing_basenames:
        max_version = 0
        if file_extension:
            extension_index = file_basename.rfind('.' + file_extension)
            regex_string = re.escape(file_basename[0:extension_index]) + '-?(?P<version>\d*)' + file_basename[extension_index::]
        else:
            regex_string = re.escape(file_basename) + '-?(?P<version>\d*)'
        regex = re.compile(regex_string)
        print('regex string: ' + regex_string)
        if extension_index > -1:
            new_file_basename = find_unique_name(existing_basenames, file_basename, regex, extension_index)
        else:
            new_file_basename = find_unique_name(existing_basenames, file_basename, regex)
    else:
        new_file_basename = file_basename

    shutil.copy(filepath, os.path.join(destination_folder, new_file_basename))
    return new_file_basename
