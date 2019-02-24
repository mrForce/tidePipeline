from Bio import SeqIO
from Bio.Alphabet import IUPAC
import re
import subprocess
import os
import glob
import re
import shutil
from collections import defaultdict

"""
A keyword argument is peptides_format = True

For context, pass in the number of amino acids you want to insert into the header before and after the peptide
"""
def extract_peptides(path, length = None, *, context = 0, file_format = 'FASTA'):
    peptides = set()
    """Making a class to facilite code re-use"""
    class PeptideHandler:
        def __init__(self, length = None):
            self.peptides = defaultdict(list)
            self.length = length
        def add(self, sequence, header):
            sequence = str(sequence)
            if self.length:
                if len(sequence) >= self.length:
                    for i in range(0, len(sequence) - self.length + 1):
                        peptide = str(sequence[i:(i + self.length)])
                        if all([x in IUPAC.IUPACProtein.letters for x in peptide]):
                            header_copy = str(header) + '|%d' % i
                            if context:
                                before = sequence[max(0, i - context):i].rjust(context, '-')
                                after = sequence[(i + length):min(i + length + context, len(sequence))].ljust(context, '-')
                                header_copy = '%s|before=%s|after=%s' % (header_copy, before, after)
                            self.peptides[str(peptide)].append(header_copy)
            else:
                self.peptides[sequence].append(header + '|0')

        def get_peptides(self):
            return self.peptides

    peptide_handler = PeptideHandler(length)
    with open(path, 'rU') as handle:
        if file_format == 'FASTA':
            for record in SeqIO.parse(handle, 'fasta'):
                sequence = record.seq
                header = record.id
                peptide_handler.add(sequence, header)
                
        elif file_format == 'peptides':
            for line in handle:
                sequence = line.strip()
                peptide_handler.add(sequence, header='')
        else:
            assert(False)
    
    return peptide_handler.get_peptides()

def write_peptides(file_path, peptides, output_fasta= False):
    with open(file_path, 'w') as f:
        for peptide, headers in peptides.items():
            if output_fasta:
                #insert the FASTA header here.
                f.write('>' + '@@'.join(headers)  + '\n' + peptide + '\n')
            else:
                f.write(peptide + '\n')

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
