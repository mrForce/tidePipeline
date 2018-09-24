import configparser
import tempfile
import numpy as np

import TideEngine
import Base
import MSGFPlusEngine
import PostProcessing
import traceback
from collections import defaultdict
import DB
import argparse
import sys
import os
import Runners
from abc import ABC, abstractmethod
import networkx as nx
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg

import re
number = 0
class AbstractNode:
    @abstractmethod
    def get_text(self):
        pass
    @abstractmethod
    def get_child_nodes(self):
        pass
    def __str__(self):
        return self.get_text()
    def __repr__(self):
        return self.get_text()

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
        text =  self.index_name + '\ncontaminant sets: ' + ', '.join(self.contaminant_sets)
        if self.param_file:
            text += '\nparam file: ' + self.param_file
        if self.options:
            for option, value in self.options.items():
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
        text =  self.search_name + '\nmgf name: ' + self.mgf_name
        if self.param_file:
            text += '\nparam file: ' + self.param_file
        if self.options:
            for option, value in self.options:
                text += '\n' + option + ': ' + value
        return text
    def get_child_nodes(self):
        return [('', node) for node in self.post_process_nodes]

class ExportNode(AbstractNode):
    def __init__(self, threshold, peptides_location, contaminants_location = None):
        self.peptides_location = peptides_location
        self.contaminants_location = contaminants_location
        self.threshold = threshold
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
        self.export_nodes = []
    def set_export_nodes(self, nodes):
        self.export_nodes = nodes
    def get_text(self):
        text = self.post_processing_type
        if self.param_file:
            text += '\nparam file: ' + self.param_file
        if self.options:
            for option, value in self.options:
                text += '\n' + option + ': ' + value
        return text
    def get_child_nodes(self):
        return [(str(node.threshold), node) for node in self.export_nodes]

def add_node_to_graph(graph, parent_node, node_labels, number = 0):
    graph.add_node(parent_node, id=number)
    node_labels[parent_node] = parent_node.get_text()
    if parent_node.get_child_nodes():
        for edge_label, node in parent_node.get_child_nodes():
            add_node_to_graph(graph, node, node_labels, number + 1)
            graph.add_edge(parent_node, node, label=edge_label)
    
class TestRunTree:
    def __init__(self, source_node):
        self.graph = nx.DiGraph()
        self.node_labels = {}
        add_node_to_graph(self.graph, source_node, self.node_labels)
    def display_tree(self, image_location):
        A = nx.nx_agraph.to_agraph(nx.convert_node_labels_to_integers(self.graph, 0, 'default', 'label'))
        A.layout('dot')
        
        A.draw(image_location)


        
        

class Index:
    def __init__(self, section):
        required_params=  ['indextype', 'sourcetype', 'sourcename']
        print('section')
        print(section)
        print('type: ' + str(type(section)))
        for x in required_params:
            assert(x in section)
        self.indexType = section['indextype']
        assert(self.indexType in ['tide', 'msgf'])
        self.sourceType = section['sourcetype']
        assert(self.sourceType in ['FilteredNetMHC', 'PeptideList', 'TargetSet'])
        self.sourceName = section['sourcename']
        if 'paramfile' in section:
            self.indexParamFile = section['paramfile']
        else:
            assert(self.indexType == 'msgf')
        
        self.contaminants = section.getList('contaminants', [])
        self.memory = section.getint('memory', 0)
            
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
            index_name = self.sourceName + '_TideIndex_' + self.indexParamFile
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
            if self.memory:
                if not test_run:
                    project.create_index(self.sourceType, self.sourceName, runner, index_name, self.contaminants, self.memory)
                index_node = IndexNode(self.indexType, index_name, self.contaminants, options = {'memory': self.memory})
            else:
                if not test_run:
                    project.create_index(self.sourceType, self.sourceName, runner, index_name, self.contaminants)
                index_node = IndexNode(self.indexType, index_name, self.contaminants)
        return (project, index_name, index_node, source_node)
    



class Search:
    def __init__(self, section, searchType):
        assert('mgfname' in section)
        print('section')
        print(section)
        self.mgfName = section['mgfname']
        self.searchType = searchType
        if 'paramfile' in section:
            self.searchParamFile = section['paramfile']
        else:
            assert(searchType == 'msgf')
        self.options = {}
        self.searchNumber = section.getint('searchnumber', -1)
        assert(self.searchNumber > -1)
        self.memory = section.getint('memory', 0)
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
            print('search name: ' + search_name)
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
            print('search name: ' + search_name)
            num = 1
            if search_name in search_names:
                while (search_name + str(num)) in search_names:
                    num += 1
                search_name = search_name + str(num)
            param_file_row = project.get_tide_search_parameter_file(self.searchParamFile)
            runner = Runners.TideSearchRunner(crux_exec_path, project.project_path, param_file_row)
            if not test_run:
                project.run_search(self.mgfName, index_name, runner, search_name)
            search_node = SearchNode(self.searchType, search_name, self.mgfName, param_file = self.searchParamFile)
        else:
            assert(False)
        return (search_name, search_node)





class PostProcess:
    def __init__(self, section, searchNumMap):
        required_params = ['postprocesstype', 'searchnumber', 'cutoffsandlocations']
        print('section')
        print(section)
        for param in required_params:
            print('param: ' + param)
            
            assert(param in section)
        self.postProcessType = section['postprocesstype']
        assert(self.postProcessType in ['percolator', 'assign-confidence', 'msgf'])
        searchNumber = section.getint('searchnumber', -1)
        self.searchNumMap = searchNumMap
        
        assert(searchNumber in self.searchNumMap)
        self.searchName = searchNumMap[searchNumber][0]
        self.searchNumber = searchNumber
        self.searchType = searchNumMap[searchNumber][1]
        """
        Just a bunch of comma seperated tuples of the form (cutoff, peptide output, [contaminant output])
        """
        print('section')
        print(section)
        self.cutoffsAndLocations = section.getTuples('cutoffsandlocations', [])
        print('self.cutoffsAndLocations')
        print(self.cutoffsAndLocations)
        cutoffs = [x[0] for x in self.cutoffsAndLocations]
        assert(len(cutoffs) == len(set(cutoffs)))
        peptide_locations = [x[1] for x in self.cutoffsAndLocations]
        assert(len(peptide_locations) == len(set(cutoffs)))
        contaminant_locations = list(filter(lambda x: x, [x[2] if len(x) == 3 else False for x in self.cutoffsAndLocations]))
        assert(len(contaminant_locations) == len(set(contaminant_locations)))
        assert(self.cutoffsAndLocations)
        assert(self.searchNumber > -1)
        if 'paramfile' in section:
            self.postProcessParamFile = section['paramfile']
        else:
            self.postProcessParamFile = None
            assert(self.postProcessType == 'msgf')
    def run_post_process_and_export(self, project, test_run = False):
        crux_exec_path = project.get_crux_executable_path()
        post_processor_names = []
        filtered_names = []
        runner = None
        export_nodes = []
        post_process_name = self.searchName + '_' + self.postProcessType
        if self.postProcessType == 'percolator':
            project.verify_row_existence(DB.PercolatorParameterFile.Name, self.postProcessParamFile)
            parameter_file_row = project.get_percolator_parameter_file(self.postProcessParamFile)
            runner = Runners.PercolatorRunner(crux_exec_path, project.project_path, parameter_file_row)
            post_processor_names = project.get_column_values(DB.Percolator, 'PercolatorName')
            if post_process_name in post_processor_names:
                num = 1
                while (post_process_name + '_' + str(num)) in post_processor_names:
                    num += 1
                post_process_name = post_process_name + '_' + str(num)
            if not test_run:
                #PostProcess.py percolator function expects msgfplus or tide. 
                searchtype_converter = {'tide': 'tide', 'msgf': 'msgfplus'}
                project.percolator(self.searchName, searchtype_converter[self.searchType], runner, post_process_name)
                print('ran percolator on searchName: ' + self.searchName + ' with search type: ' + self.searchType)
                assert(project.verify_row_existence(DB.Percolator.PercolatorName, post_process_name))
        elif self.postProcessType == 'assign-confidence':
            project.verify_row_existence(DB.AssignConfidenceParameterFile.Name, self.postProcessParamFile)
            parameter_file_row = project.get_assign_confidence_parameter_file(self.postProcessParamFile)
            runner = Runners.AssignConfidenceRunner(crux_exec_path, project.project_path, parameter_file_row)
            post_processor_names = project.get_column_values(DB.AssignConfidence, 'AssignConfidenceName')
            if post_process_name in post_processor_names:
                num = 1
                while (post_process_name + '_' + str(num)) in post_processor_names:
                    num += 1
                post_process_name = post_process_name + '_' + str(num)
            
            project.assign_confidence(self.searchName, runner, post_process_name)
            assert(project.verify_row_existence(DB.AssignConfidence.AssignConfidenceName, post_process_name))
        for tup in self.cutoffsAndLocations:
            cutoff = tup[0]
            peptide_output = tup[1]
            contaminant_output = None
            if len(tup) == 3:
                contaminant_output = tup[2]
            filter_node = None
            export_node = ExportNode(str(cutoff), peptide_output, contaminant_output)
            export_nodes.append(export_node)
            
            print('post process name: ' + post_process_name)            
            filtered_name = post_process_name + '_' + str(cutoff)
            
            if filtered_name in filtered_names:
                num = 1
                while (filtered_name + '_' + str(num)) in filtered_names:
                    num += 1
                filtered_name = filtered_names + '_' + str(num)


            if self.postProcessType == 'percolator':
                if not test_run:                    
                    project.filter_q_value_percolator(post_process_name, cutoff, filtered_name, True)
            elif self.postProcessType == 'assign-confidence':
                if not test_run:                    
                    project.filter_q_value_assign_confidence(post_process_name, cutoff, post_process_name)            
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
        post_processor_node.set_export_nodes(export_nodes)
        return post_processor_node

    

    
                    
class JordanDict(dict):
    def getint(self, option, default = 0):
        if option in self:
            return int(self[option])
        else:
            return default
    def getList(self, option, default = []):
        if option in self:
            line = self[option]
            trimmed_pieces = [piece.strip() for piece in line.split(',')]
            return trimmed_pieces
        else:
            return []
    def getTuples(self, option, default = []):
        if option not in self:
            return default
        line = self[option]
        regex = re.compile('\(([^\)]+)\)')
        tuple_strings = regex.findall(line)
        tuples = []
        for inside_string in tuple_strings:
            parts = [piece.strip() for piece in inside_string.split(',')]
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
        return tuples
def run_pipeline(ini_file, project_folder, image_location, test_run = False):
    config = configparser.ConfigParser(dict_type = JordanDict)
    config.read(ini_file)
    print('going to get sections')
    sections = config._sections
    
    print('sections')
    print(type(sections))

    index_section = sections['Index']
    search_sections = []
    postprocess_sections = []
    for key, value in sections.items():
        if key.startswith('Search'):
            search_sections.append(value)
        elif key.startswith('PostProcess'):
            postprocess_sections.append(value)
    print('index section')
    print(index_section)
    index_object = Index(index_section)
    index_type = index_object.indexType
    """
    DON'T FORGET TO ADD THE CHILD NODES LATER ON!
    """
    project, index_name, index_node, peptide_source_node = index_object.create_index(project_folder, test_run)
    post_process_nodes = []
    searchNumMap = {}
    searchNumToNodeMap = {}
    
    for search_section in search_sections:
        search_object = Search(search_section, index_type)
        search_name, search_node = search_object.run_search(project, index_name, test_run)
        searchNumMap[search_object.searchNumber] = (search_name, index_type)
        searchNumToNodeMap[search_object.searchNumber] = search_node

    project.end_command_session()
    project = PostProcessing.PostProcessing(project_folder, '')
    for post_process_section in postprocess_sections:
        post_process_object = PostProcess(post_process_section, searchNumMap)
        post_process_node =  post_process_object.run_post_process_and_export(project, test_run)
        searchNumToNodeMap[post_process_object.searchNumber].add_post_process_node(post_process_node)
    search_nodes = list(searchNumToNodeMap.values())
    index_node.set_search_nodes(search_nodes)
    peptide_source_node.set_index_nodes([index_node])
    tree = TestRunTree(peptide_source_node)
    tree.display_tree(image_location)
