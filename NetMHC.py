import re
import os
import subprocess
import time
import shutil
def parse_netmhc(netmhc_output_path, parse_output_path):
    regex = re.compile('^(\s+[^\s]+){2}(\s+(?P<peptide>[A-Z]+))(\s+[^\s]+){10}(\s+(?P<rank>[0-9]{1,2}\.[0-9]+))')
    results = []
    with open(netmhc_output_path, 'r') as f:
        with open(parse_output_path, 'w') as g:
            for line in f:
                match = regex.match(line)
                if match:
                    g.write(match.group('peptide') + ',' + match.group('rank') + '\n')

def get_num_lines(filepath):
    wc_process = subprocess.run(['wc', filepath], stdout=subprocess.PIPE)
    return int(wc_process.stdout.decode().split()[0])
def call_netmhc(hla, peptide_file_path, output_path):
    num_peptides = get_num_lines(peptide_file_path)
    """
    We need to split the file (into 2000 line files), because it seems that NetMHC has a hard time handling large files. It's not open source, so I'm not entirely sure why, and I don't really have a good way to investigate it.

    
    """
    peptide_file_name = os.path.split(peptide_file_path)[1]
    os.makedirs(peptide_file_path + '-parts')
    f = open(output_path, 'w')
    folder = peptide_file_path + '-parts'
    new_peptide_path = os.path.join(folder, peptide_file_name)
    shutil.copyfile(peptide_file_path, new_peptide_path)
    cwd = os.getcwd()
    os.chdir(folder)
    files_before  = set(os.listdir())
    print('Going to run split on: ' + peptide_file_name + ' inside of: ' + os.getcwd())
    subprocess.run(['split', '-l', '5000', peptide_file_name])
    os.remove(peptide_file_name)
    start_time = time.time()
    files = list(set(os.listdir()) - files_before)
    progress = 0.0
    num_files = len(files)
    i = 0
    progress = 0.0
    for filename in files:
        print('going to run netmhc fromt: ' + os.getcwd() + ' on file: ' + filename)
        
        subprocess.run(['/usr/bin/netmhc', '-a', hla, '-f', filename, '-p'], stdout=f)
        i += 1
        new_progress = 100.0*i/num_files
        if new_progress - progress >= 1.0:
            time_taken = time.time() - start_time
            eta = 1.0*time_taken/i*(num_files - i)
            progress = new_progress
            print('Progress: ' + str(progress) + '% eta: ' + str(eta) + ' seconds')
    f.close()
    os.chdir(cwd)
