import json
from collections import Counter
def count_sources(project_path, target_set_row, peptides):
    source_id_map = json.loads(target_set_row.SourceIDMap)
    peptide_source_map_path= target_set_row.PeptideSourceMapPath
    source_count = Counter()
    id_to_string = {}
    for k, v in source_id_map['filtered_netmhc'].items():
        id_to_string[int(k)] = 'FilteredNetMHC_' + v
    for k, v in source_id_map['peptide_lists'].items():
        id_to_string[int(k)] = 'PeptideList_' + v
    with open(os.path.join(project_path, peptide_source_map_path), 'r')  as f:
        peptide_source_map = json.load(f)
        for peptide in peptides:
            assert(peptide in peptide_source_map)
            if isinstance(peptide_source_map[peptide], list):
                source_count[set([int(x) for x in peptide_source_map[peptide]])] += 1
            else:
                source_count[set([int(x)])] += 1

    counts = {}
    for s, count in source_count.items():
        
