import configparser
import TideEngine
import Base
import MSGFPlusEngine
from collections import defaultdict
import DB
import argparse
import sys
import os
import Runners
from abc import ABC, abstractmethod
import networkx as nx
import matplotlib.pyplot as plt

class AbstractNode(ABC):
    @abstractmethod
    def get_text(self):
        pass
    @abstractmethod
    def get_child_nodes(self):
        pass

class PeptideSourceNode(AbstractNode):
    def __init__(self, sourceType, sourceName):
        self.sourceType = sourceType
        self.sourceName = sourceName
        self.index_nodes = []
    def get_text(self):
        return self.sourceType + '.' + self.sourceName
    def set_index_nodes(self, nodes):
        self.index_nodes = nodes
    def get_child_nodes(self):
        return [('', node) for node in self.index_nodes]

class IndexNode(AbstractNode):
    def __init__(self, index_type, index_name, contaminant_sets, *, param_file = None, options = None):
        self.index_type = index_type
        self.index_name = index_name
        self.contaminant_sets = contaminant_sets
        self.param_file = param_file
        self.options = options
        self.search_nodes = []
    def set_search_nodes(self, search_nodes):
        self.search_nodes = search_nodes
    def get_text(self):
        text = self.index_type + '.' + self.index_name + '\ncontaminant sets: ' + ', '.join(self.contaminant_sets)
        if self.param_file:
            text += '\nparam file: ' + self.param_file
        if self.options:
            for option, value in self.options:
                text += '\n' + option + ': ' + value
        return text
    def get_child_nodes(self):
        return [('', node) for node in self.search_nodes]

class SearchNode(AbstractNode):
    def __init__(self, search_type, search_name, mgf_name,  *, param_file = None, options = None):
        self.search_type = search_type
        self.search_name = search_name
        self.mgf_name = mgf_name
        self.param_file = param_file
        self.options = options
        self.post_process_nodes = []
    def set_post_process_nodes(self, nodes):
        self.post_process_nodes = nodes
    def add_post_process_node(self, node):
        self.post_process_nodes.append(node)
    def get_text(self):
        text = self.search_type + '.' + self.search_name + '\nmgf name: ' + self.mgf_name
        if self.param_file:
            text += '\nparam file: ' + self.param_file
        if self.options:
            for option, value in self.options:
                text += '\n' + option + ': ' + value
        return text
    def get_child_nodes(self):
        return [('', node) for node in self.post_process_nodes]

class ExportNode(AbstractNode):
    def __init__(self, peptides_location, contaminants_location = None):
        self.peptides_location = peptides_location
        self.contaminants_location = contaminants_location
    def get_text(self):
        text = self.peptides_location
        if self.contaminants_location:
            text += '\n' + self.contaminants_location
        return text
    def get_child_nodes(self):
        return []


    
class FilterNode(AbstractNode):
    def __init__(self, filter_name, threshold):
        self.filter_name = filter_name
        self.threshold = threshold
        self.export_nodes = []
    def set_export_nodes(self, nodes):
        self.export_nodes = nodes
    def get_text(self):
        return self.filter_name
    def get_child_nodes(self):
        return [('', node) for node in self.export_nodes]
class PostProcessingNode(AbstractNode):
    def __init__(self, post_processing_type, post_processing_name, search_num, *, param_file = None, options = None):
        self.post_processing_type = post_processing_type
        self.post_processing_name = post_processing_name
        self.param_file = param_file
        self.options = options
        self.filter_nodes = []
    def set_filter_nodes(self, nodes):
        self.filter_nodes = nodes
    def get_text(self):
        text = self.post_processing_type + '.' + self.post_processing_name
        if self.param_file:
            text += '\nparam file: ' + self.param_file
        if self.options:
            for option, value in self.options:
                text += '\n' + option + ': ' + value
        return text
    def get_child_nodes(self):
        return [(str(node.threshold), node) for node in self.filter_nodes]

def add_node_to_graph(graph, parent_node):
    graph.add_node(parent_node)
    if parent_node.get_child_nodes():
        for edge_label, node in parent_node.get_child_nodes():
            add_node_to_graph(graph, node)
            graph.add_edge(parent_node, node, label=edge_label)
    
class TestRunTree:
    def __init__(self, source_node):
        self.graph = nx.Graph()
        add_node_to_graph(self.graph, source_node)
    def display_tree(self):
        plot = nx.spring_layout(self.graph)
        nx.draw(self.graph, plot)
        edge_labels = nx.get_edge_attributes(self.graph, 'label')
        nx.draw_networkx_edge_labels(self.graph, plot, edge_labels)
        plt.show()
        
        

class Index:
    def __init__(self, section):
        required_params=  ['indexType', 'sourceType', 'sourceName']
        for x in required_params:
            assert(x in section)
        self.indexType = section['indexType']

        assert(self.indexType in ['tide', 'msgf'])
        self.sourceType = section['sourceType']
        assert(self.sourceType in ['FilteredNetMHC', 'PeptideList', 'TargetSet'])
        self.sourceName = section['sourceName']
        if 'paramFile' in section:
            self.indexParamFile = section['paramFile']
        else:
            assert(self.indexType == 'msgf')
        if 'netmhcdecoys' in section:
            self.netmhcdecoys  = section['netmhcdecoys']
        else:
            self.netmhcdecoys = None
        self.contaminants = section.getList('contaminants', [])
        self.memory = section.get_int('memory', 0)
            
    """
    Creates an instance of either MSGFPlusEngine or TideEngine, and returns it. It also returns the name of the index.

    Returns a tuple. 
    """
    def create_index(self, project_folder, test_run = False):
        source_node = PeptideSourceNode(self.sourceType, self.sourceName)
        project = None
        index_name = None
        index_names = []
        if self.indexType == 'tide':
            project = TideEngine.TideEngine(project_folder, '')
            index_names = project.get_column_values(DB.TideIndex, 'TideIndexName')
            index_name = self.sourceName + '_TideIndex_' + self.indexParamFile + '_'
        elif self.indexType == 'msgf':
            project = MSGFPlusEngine.MSGFPlusEngine(project_folder, '')
            index_names = project.get_column_values(DB.MSGFPlusIndex, 'MSGFPlusIndexName')
            index_name = self.sourceName + '_MSGFPlusIndex'
            
        else:
            assert(False)
        if index_name in index_names:
            num = 1
            while (index_name + str(num)) in index_names:
                num += 1
            index_name = index_name + str(num)
        crux_exec_path = project.get_crux_executable_path()
        msgf_exec_path = project.get_msgfplus_executable_path()
        if self.sourceType == 'FilteredNetMHC':
            assert(project.verify_filtered_netMHC(self.sourceName))
        elif self.sourceType == 'PeptideList':
            assert(project.verify_peptide_list(self.sourceName))
        elif self.sourceType == 'TargetSet':
            assert(project.verify_target_set(self.sourceName))
        else:
            assert(False)
        project.begin_command_session()
        index_node = None
        if self.indexType == 'tide':
            index_node = IndexNode(self.indexType, index_name, self.contaminants, param_file = self.indexParamFile)
            param_file_row = project.get_tide_index_parameter_file(self.indexParamFile)
            assert(param_file_row is not None)
            runner = Runners.TideIndexRunner({}, crux_exec_path, project.project_path, param_file_row)
            if not test_run:
                if self.contaminants:
                    project.create_index(self.sourceType, self.sourceName, runner, index_name, self.contaminants)
                else:
                    project.create_index(self.sourceType, self.sourceName, runner, index_name)
        elif self.indexType == 'msgf':
            runner = Runners.MSGFPlusIndexRunner(msgf_exec_path)
            if self.netmhcdecoys:
                netmhc_row = project.get_netmhc_row(self.netmhcdecoys)
                parsed_location = os.path.abspath(os.path.join(project_folder, netmhc_row.PeptideRankPath))
                self.netmhcdecoy_name = self.netmhcdecoys
                self.netmhcdecoys = (parsed_location, netmhc_row)                
            if self.memory:
                if not test_run:
                    project.create_index(self.sourceType, self.sourceName, runner, index_name, self.contaminants, self.memory, netmhc_decoys = self.netmhcdecoys)
                options = {'memory': self.memory}
                if self.netmhcdecoys:
                    options['netMHCDecoys'] = self.netmhcdecoy_name
                index_node = IndexNode(self.indexType, index_name, self.contaminants, options = options)
            else:
                if not test_run:
                    project.create_index(self.sourceType, self.sourceName, runner, index_name, self.contaminants, netmhc_decoys = self.netmhcdecoys)
                if self.netmhcdecoys:
                    index_node = IndexNode(self.indexType, index_name, self.contaminants, options={'netMHCDecoys': self.netmhcdecoy_name})
                else:
                    index_node = IndexNode(self.indexType, index_name, self.contaminants)
        return (project, index_name, index_node, source_node)
    



class Search:
    def __init__(self, section, searchType):
        assert('mgfName' in section)
        assert('searchNumber' in section)
        self.mgfName = section['mgfName']
        self.searchType = searchType
        if 'paramFile' in section:
            self.searchParamFile = section['paramFile']
        else:
            assert(searchType == 'msgf')
        self.options = {}
        self.searchNumber = section.get_int('searchNumber', -1)
        assert(self.searchNumber > -1)
        self.memory = section.get_int('memory', 0)
        if searchType == 'msgf':
            keys = Runners.MSGFPlusSearchRunner.converter.keys()
            for key in keys:
                if key in section and section[key]:
                    self.options[key] = section[key]
    """
    returns the name of the search, and the search node.
    """ 
    def run_search(self, project, index_name, test_run = False):
        search_names = project.get_column_values(DB.SearchBase, 'SearchName')
        search_name = None
        search_node = None
        if self.searchType == 'msgf':
            if not test_run:
                assert(project.verify_row_existence(DB.MSGFPlusIndex.MSGFPlusIndexName, index_name))
            msgfplus_jar = project.executables['msgfplus']
            runner = Runners.MSGFPlusSearchRunner(self.options, msgfplus_jar)
            search_name = index_name + '_msgf_' + self.mgfName
            num = 1
            if search_name in search_names:
                while (search_name + str(num)) in search_names:
                    num += 1
                search_name = search_name + str(num)
            if self.memory:
                if not test_run:
                    project.run_search(self.mgfName, index_name, None, runner, search_name, self.memory)
                search_node = SearchNode(self.searchType, search_name, self.mgfName, options = self.options + {'memory': self.memory})
            else:
                if not test_run:
                    project.run_search(self.mgfName, index_name, None, runner, search_name)
                search_node = SearchNode(self.searchType, search_name, self.mgfName, options = self.options)
        elif self.searchType == 'tide':
            if not test_run:
                assert(project.verify_row_existence(DB.TideIndex.TideIndexName, index_name))
            crux_exec_path = project.get_crux_executable_path()
            search_name = index_name + '_tide_' + self.mgfName
            num = 1
            if search_name in search_names:
                while (search_name + str(num)) in search_names:
                    num += 1
                search_name = search_name + str(num)
            param_file_row = project.get_tide_search_parameter_file(self.searchParamFile)
            runner = Runners.TideSearchRunner(crux_exec_path, project.project_path, param_file_row)
            if not test_run:
                project.run_search(self.mgfName, index_name, runner, search_name)
            search_node = SearchNode(self.searchType, search_name, self.mgfName, param_file = param_file_row)
        else:
            assert(False)
        return (search_name, search_node)





class PostProcess:
    def __init__(self, section, searchNumMap):
        required_params = ['postProcessType', 'searchNum', 'cutoffsAndLocations']
        for param in required_params:
            assert(param in section)
        self.postProcessType = section['postProcessType']
        assert(self.postProcessType in ['percolator', 'assign-confidence', 'msgf'])
        searchNum = section.get_int('searchNum', -1)
        self.searchNumMap = searchNumMap
        assert(searchNum in self.searchNumMap)
        self.searchName = self.searchNumMap[searchNum][0]
        self.searchNumber = searchNum
        self.searchType = self.searchNumMap[searchNum][1]
        """
        Just a bunch of comma seperated tuples of the form (cutoff, peptide output, [contaminant output])
        """
        self.cutoffsAndLocations = section.get_tuples('cutoffsAndLocations', [])
        cutoffs = [x[0] for x in self.cutoffsAndLocations]
        assert(len(cutoffs) == len(set(cutoffs)))
        peptide_locations = [x[1] for x in self.cutoffsAndLocations]
        assert(len(peptide_locations) == len(set(cutoffs)))
        contaminant_locations = filter(lambda x: len(x), [x[2] if len(x) == 3 else False for x in self.cutoffsAndLocations])
        assert(len(contaminant_locations) == len(set(contaminant_locations)))
        assert(self.cutoffsAndLocations)
        assert(self.searchNumber > -1)
        if 'paramFile' in section:
            self.postProcessParamFile = section['paramFile']
        else:
            self.postProcessParamFile = None
            assert(self.postProcessType == 'msgf')
    def run_post_process_and_export(self, project, test_run = False):
        crux_exec_path = project.get_crux_executable_path()
        post_processor_names = []
        filtered_names = []
        runner = None

        filter_nodes = []
        if self.postProcessType == 'percolator':
            project.verify_row_existence(DB.PercolatorParameterFile, self.postProcessParamFile)
            parameter_file_row = project.get_percolator_parameter_file(self.postProcessParamFile)
            runner = Runners.PercolatorRunner(crux_exec_path, project.project_path, parameter_file_row)
            post_processor_names = project.get_column_values(DB.Percolator, 'PercolatorName')
        elif self.postProcessType == 'assign-confidence':
            project.verify_row_existence(DB.AssignConfidenceParameterFile, self.postProcessParamFile)
            parameter_file_row = project.get_assign_confidence_parameter_file(self.postProcessParamFile)
            runner = Runners.AssignConfidenceRunner(crux_exec_path, project.project_path, parameter_file_row)
            post_processor_names = project.get_column_values(DB.AssignConfidence, 'AssignConfidenceName')
        for tup in self.cutoffsAndLocations:
            cutoff = tup[0]
            peptide_output = tup[1]
            contaminant_output = None
            if len(tup) == 3:
                contaminant_output = tup[2]
            filter_node = None
            export_node = ExportNode(peptide_output, contaminant_output)
            post_process_name = self.searchName + '_' + self.postProcessType
            if post_process_name in post_processor_names:
                num = 1
                while (post_process_name + '_' + str(num)) in post_processor_names:
                    num += 1
                post_process_name = post_process_name + '_' + str(num)
            filtered_name = post_process_name + '_' + str(cutoff)
            
            if filtered_name in filtered_names:
                num = 1
                while (filtered_name + '_' + str(num)) in filtered_names:
                    num += 1
                filtered_name = filtered_names + '_' + str(num)
            filtered_node = FilterNode(filtered_name, str(cutoff))
            filtered_node.set_export_nodes([export_node])
            filter_nodes.append(filtered_node)
            if self.postProcessType == 'percolator':
                if not test_run:
                    project.percolator(self.searchName, self.searchType, runner, post_process_name)
                    assert(project.verify_row_existence(DB.Percolator.PercolatorName, post_process_name))
                    project.filter_q_value_percolator(post_process_name, cutoff, filtered_name, True)
            elif self.postProcessType == 'assign-confidence':
                if not test_run:
                    project.assign_confidence(self.searchName, runner, post_process_name)
                    assert(project.verify_row_existence(DB.AssignConfidence.AssignConfidenceName, filtered_name))
                    project.filter_q_value_assign_confidence(post_process_name, cutoff, filtered_name)            
            elif self.postProcessType == 'msgf':
                if not test_run:
                    project.filter_q_value_msgfplus(self.searchName, cutoff, filtered_name)
            if not test_run:
                assert(project.verify_row_existence(DB.FilteredSearchResult.filteredSearchResultName, filtered_name))
                row = project.get_filtered_search_result_row(filtered_name)
                contaminant_sets = row.get_contaminant_sets()
                contaminant_peptides = set()
                if contaminant_sets:
                    for contaminant_set in contaminant_sets:
                        peptide_file = os.path.join(project.project_path, contaminant_set.peptide_file)
                        with open(peptide_file, 'r') as f:
                            for line in f:
                                line = line.strip()
                                if len(line) > 1:
                                    contaminant_peptides.add(line)
                peptides = row.get_peptides(project.project_path)
                contaminant_file = None
                if contaminant_output:
                    contaminant_file = open(contaminant_output, 'w')
                with open(peptide_output, 'w') as f:
                    for peptide in list(peptides):
                        if peptide not in contaminant_peptides:
                            f.write(peptide + '\n')
                        elif contaminant_file:
                            contaminant_file.write(peptide + '\n')                            
                if contaminant_file:
                    contaminant_file.close()
        post_processor_node = PostProcessingNode(self.postProcessType, post_process_name, self.searchNumber, param_file = self.postProcessParamFile)
        return post_processor_node
"""
Comma seperated string
"""
def convert_list_strings(line):
    trimmed_pieces = [piece.trim() for piece in line.split(',')]
    return trimmed_pieces
"""
A list of tuples, with elements that are either strings, integers, or floats
"""
def convert_list_tuples(line):
    tuple_strings = [piece.trim() for piece in line.split(',')]
    tuples = []
    for tuple_string in tuple_strings:
        assert(tuple_string.startswith('('))
        assert(tuple_string.startswith(')'))
        inside_string = tuple_string[1:-1]
        parts = [piece.trim() for piece in line.split(',')]
        start_list = []
        for part in parts:
            if part.isdigit():
                start_list.append(int(part))
            else:
                try:
                    start_list.append(float(part))
                except:
                    start_list.append(part)
        tuples.append(tuple(start_list))
                    
class ListDict(dict):     
    def __setitem__(self, key, value):
        if key in self:
            self.__getitem__(key).append(value)
        else:
            super().__setitem__(key, [value])
    

def run_pipeline(ini_file, project_folder, test_run = False):
    config = configparser.ConfigParser(dict_type = ListDict, strict=False)
    config.read(ini_file)
    assert('Index' in config)
    index_section = config['Index']
    index_object = Index(index_section)
    index_type = index_object.indexType
    """
    DON'T FORGET TO ADD THE CHILD NODES LATER ON!
    """
    project, index_name, index_node, peptide_source_node = index_object.create_index(project_folder, test_run)
    post_process_nodes = []
    searchNumMap = {}
    searchNumToNodeMap = {}
    for search_section in config['Search']:
        search_object = Search(search_section, index_type)
        search_name, search_node = search_object.run_search(project, index_name, test_run)
        searchNumMap[search_object.searchNumber] = search_name
        searchNumToNodeMap[search_object.searchNumber] = search_node
    for post_process_section in config['PostProcess']:
        post_process_object = PostProcess(post_process_section, searchNumMap)
        post_process_node =  post_process_object.run_post_process_and_export(project, test_run)
        searchNumToNodeMap[post_process_object.searchNumber].add_post_process_node(post_process_node)
    search_nodes = list(searchNumToNodeMap.values())
    index_node.set_search_nodes(search_nodes)
    peptide_source_node.set_index_nodes([index_node])
    tree = TestRunTree(peptide_source_node)
    tree.display_tree()
