from collections import defaultdict
import os
import json
"""
The filtered_netmhc argument is a list of the form [(name, location)...], where name is the name of the FilteredNetMHC entry, and location is the location of filtered peptides (the fasta_path field in the FilteredNetMHC table). 

The peptide_lists argument is also a list of the form [(name, location)...], where name is the name of the PeptideList entry, and the location is the location of the peptides (the PeptideListPath field in the PeptideList table).

output_fasta_location is where we store the unique set of targets in FASTA format (so that it can easily be passed into tide-index). 

output_json_location is the path to a (not yet created) file that will store the JSON dictionary mapping each target to its source(s). Each target will be mapped either to a single number, or to a list of numbers. Each number will correspond to either an entry from the filtered_netmhc, or an entry from peptide_lists. 

This function returns a dictionary of the form {'filtered_netmhc': {number: 'name',...}, 'peptide_lists': {number: 'name', ...}}


"""

def create_target_set(filtered_netmhc, peptide_lists, output_fasta_location, output_json_location):
    assert(not os.path.isfile(output_fasta_location))
    assert(not os.path.isdir(output_fasta_location))
    assert(not os.path.isfile(output_json_location))
    assert(not os.path.isdir(output_json_location))

    with open(output_fasta_location, 'w') as f:
        pass

    
    
    with open(output_json_location, 'w') as f:
        pass
    i = 0
    filtered_map = {}
    filtered_map_reverse = {}
    for name, location, row in filtered_netmhc:
        filtered_map[i] = name
        filtered_map_reverse[name] = i
        i += 1
    peptide_lists_map = {}
    peptide_lists_map_reverse = {}
    peptide_to_header = defaultdict(list)
    for name, location in peptide_lists:
        peptide_lists_map[i] = name
        peptide_lists_map_reverse[name] = i
        i += 1
    source_id_map = {'filtered_netmhc': filtered_map, 'peptide_lists': peptide_lists_map}
    target_set = defaultdict(list)
    for name, location, row in filtered_netmhc:
        print('going to do filterednetmhc: ' + name)
        source_id = filtered_map_reverse[name]
        with open(location, 'r') as f:
            for record in SeqIO.parse(f, 'fasta'):
                peptide = str(record.seq)
                header = str(record.id)
                if len(peptide) > 0:
                    target_set[peptide].append(source_id)
                    peptide_to_header[peptide].append(header)
    for name, location in peptide_lists:
        print('going to do peptide list: ' + name)
        source_id = peptide_lists_map_reverse[name]
        with open(location, 'r') as f:
            for record in SeqIO.parse(f, 'fasta'):
                peptide = str(record.seq)
                header = str(record.id)
                if len(peptide) > 0:
                    target_set[peptide].append(source_id)
                    peptide_to_header[peptide].append(header)
    i = 0
    with open(output_fasta_location, 'w') as f:
        for target_sequence, source_list in target_set.items():
            assert(len(source_list) > 0)
            header = ' @@ '.join(peptide_to_header[target_sequence])
            f.write('>' + header + '\n')
            f.write(target_sequence + '\n')
            if len(source_list) == 1:
                target_set[target_sequence] = source_list[0]
            i += 1
    with open(output_json_location, 'w') as g:
        json.dump(dict(target_set), g)
    return source_id_map
