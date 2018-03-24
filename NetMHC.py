import re
import subprocess
import time

def parse_netmhc(netmhc_output_path, parse_output_path):
    regex = re.compile('^(\s+[^\s]+){2}(\s+(?P<peptide>[A-Z]+))(\s+[^\s]+){10}(\s+(?P<rank>[0-9]{1,2}\.[0-9]+))')
    results = []
    with open(output_file, 'r') as f:
        with open(parse_output_path, 'w') as g:
            for line in f:
                match = regex.match(line)
                if match:
                    g.write(match.group('peptide') + ',' + match.group('rank') + '\n')

def get_num_lines(filepath):
    wc_process = subprocess.run(['wc', filepath], stdout=subprocess.PIPE)
    return int(wc.stdout.decode().split()[0])
def call_netmhc(hla, peptide_file_path, output_path):
    num_peptides = get_num_lines(peptide_file_path)
    with open(output_path, 'w') as f:
        start_time = time.time()
        netmhc_process = subprocess.Popen(['netmhc', '-a', hla, '-f', peptide_file_path, '-p'], stdout=f)
        progress = 0.0
        while netmhc_process.poll() is None:
           time.sleep(10)
           num_peptides_processed = max(get_num_lines(output_path) - 5, 0)
           new_progress = 100.0*num_peptides_processed/num_peptides
           if new_progress - progress >= 1.0:
               time_taken = time.time() - start_time
               eta = 1.0*time_taken/num_peptides_processed*(num_peptides - num_peptides_processed)
               progress = new_progress
               print('Progress: ' + str(progress) + '% eta: ' + str(eta) + ' seconds')
