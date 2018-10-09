import re
import os
import subprocess
import time
import shutil
import uuid
import threading
import functools
class NetMHCCommand:
    def __init__(self, command, output_location):
        self.command = command
        self.output_location = output_location
    def get_command(self):
        return self.command
    def get_output_location(self):
        return self.output_location

class NetMHCRunner(threading.Thread):
    def __init__(self, netmhc_commands, list_lock, create_progress_string):
        threading.Thread.__init__(self)
        self.netmhc_commands = netmhc_commands
        self.list_lock = list_lock
        self.create_progress_string = create_progress_string
    def run(self):
        keep_going = True
        while keep_going:
            self.list_lock.acquire()
            print(self.create_progress_string(len(self.netmhc_commands)))
            if len(self.netmhc_commands) == 0:
                keep_going = False
                self.list_lock.release()
            else:
                netmhc_command_object = self.netmhc_commands.pop()
                self.list_lock.release()
                print('command: ' + netmhc_command_object.get_command())
                subprocess.call([netmhc_command_object.get_command() + ' > ' + netmhc_command_object.get_output_location()], shell=True)                               
                #with open(netmhc_command_object.get_output_location(), 'w') as f:
                #    subprocess.run(netmhc_command_object.get_command(), stdout=f)

        


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
    print('filepath: ' + filepath)
    wc_process = subprocess.check_output(['wc', filepath])
    return int(wc_process.decode().split()[0])
def call_netmhc(netmhc_location, hla, peptide_file_path, output_path, num_threads=2):

    #netmhc_location = '/home/code/IMPORT/netMHC-4.0/netMHC'
    num_peptides = get_num_lines(peptide_file_path)
    """
    We need to split the file (into 2000 line files), because it seems that NetMHC has a hard time handling large files. It's not open source, so I'm not entirely sure why, and I don't really have a good way to investigate it.

    
    """
    peptide_file_name = os.path.split(peptide_file_path)[1]
    folder = peptide_file_path + '-parts'
    new_peptide_path = os.path.join(folder, peptide_file_name)
    
    folder = peptide_file_path + '-parts'
    new_peptide_path = os.path.join(folder, peptide_file_name)
    cwd = os.getcwd()
    files_before = set()
    if os.path.isdir(folder):
        os.chdir(folder)
    else:
        os.makedirs(folder)
        shutil.copyfile(peptide_file_path, new_peptide_path)
        os.chdir(folder)
        files_before  = set(os.listdir())
        print('Going to run split on: ' + peptide_file_name + ' inside of: ' + os.getcwd())
        subprocess.call(['split', '-l', '10000', peptide_file_name])
        os.remove(peptide_file_name)        
    start_time = time.time()
    files = list(set(os.listdir()) - files_before)
    #we'll create a temporary folder to place the NetMHC output
    temp_folder_name = str(uuid.uuid4())
    while os.path.exists(temp_folder_name):
        temp_folder_name = str(uuid.uuid4())
    os.makedirs(temp_folder_name)
    temp_folder_abs_path = os.path.abspath(temp_folder_name)
    progress = 0.0
    num_files = len(files)
    i = 0
    progress = 0.0
    netmhc_list = []
    output_file_list = []
    for filename in files:
        output_file_path = os.path.join(temp_folder_name, filename + '-TEMPOUTPUT')
        netmhc_list.append(NetMHCCommand(netmhc_location + ' -a ' + hla + ' -f ' + filename + ' -p ', output_file_path))
        output_file_list.append(output_file_path)

    num_runs = len(netmhc_list)
    threads = []
    list_lock = threading.Lock()
    def _progress(num_runs_total, start_time, num_runs_left):
        progress = 100.0*(num_runs_total - num_runs_left)/num_runs_total
        time_taken = time.time() - start_time
        if num_runs_left > 0 and num_runs_left < num_runs_total:
            time_per_run = 1.0*time_taken/(num_runs_total - num_runs_left)
            return 'progress: ' + str(progress) + '%, eta: ' + str(time_per_run*num_runs_left) + ' seconds'
        elif num_runs_left == 0:
            return 'Complete!'
        elif num_runs_left == num_runs_total:
            return 'Starting'
    start_time = time.time()
    for t in range(0, num_threads):
        thread = NetMHCRunner(netmhc_list, list_lock, functools.partial(_progress, num_runs, start_time))
        threads.append(thread)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    os.chdir(cwd)
    subprocess.call(['bash_scripts/combine_files.sh'] + [os.path.join(folder, x) for x in output_file_list] + [output_path])
    shutil.rmtree(temp_folder_abs_path)
    
        
