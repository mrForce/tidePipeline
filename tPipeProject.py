import tPipeDB
from create_target_set import *
import sys
import tempfile
import os
from Bio import SeqIO
from NetMHC import *
import glob
import re
import shutil
import uuid
from fileFunctions import *
from datetime import datetime
import json
import TargetSetSourceCount
import ReportGeneration

from Errors import *
from Runners import *

    
    


class Project:
    def __init__(self, project_path, command):
        if os.path.isfile('reminder.txt'):
            subprocess.call(['cat', 'reminder.txt'])
        self.project_path = project_path
        print('project path: ' + project_path)
        self.db_session = tPipeDB.init_session(os.path.join(project_path, 'database.db'))
        self.command = tPipeDB.Command(commandString = command)
        self.db_session.add(self.command)
        self.db_session.commit()

    def assign_confidence_to_filtered_search_result(self, assign_confidence_name, q_value_threshold, filtered_search_result_name):
        row = self.get_assign_confidence(assign_confidence_name)
        q_val_column=  'tdc q-value'
        if row.estimation_method and len(row.estimation_method) > 0:
            q_val_column = row.estimation_method + ' q-value'
        handler = ReportGeneration.AssignConfidenceHandler(row, q_val_column, q_value_threshold, self.project_path)
        peptides = handler.getPeptides()
        filtered_filename = str(uuid.uuid4())
        while os.path.isfile(os.path.join(self.project_path, 'FilteredSearchResult', filtered_filename)) or os.path.isdir(os.path.join(self.project_path, 'FilteredSearchResult', filtered_filename)):
            filtered_filename = str(uuid.uuid4())
        with open(os.path.join(self.project_path, 'FilteredSearchResult', filtered_filename), 'w') as f:
            for peptide in peptides:
                f.write(peptide + '\n')
        filtered_row = tPipeDB.FilteredSearchResult(filteredSearchResultName = filtered_search_result_name, filteredSearchResultPath = os.path.join('FilteredSearchResult', filtered_filename), q_value_threshold = str(q_value_threshold), method='AssignConfidence')
        self.db_session.add(filtered_row)
        self.db_session.commit()

        
        
    def get_filtered_netmhc_row(self, name):
        return self.db_session.query(tPipeDB.FilteredNetMHC).filter_by(FilteredNetMHCName = name).first()

    def get_target_set_row(self, name):
        return self.db_session.query(tPipeDB.TargetSet).filter_by(TargetSetName = name).first()
    def get_peptide_list_row(self, name):
        return self.db_session.query(tPipeDB.PeptideList).filter_by(peptideListName = name).first()
    def get_filtered_search_result_row(self, name):
        return self.db_session.query(tPipeDB.FilteredSearchResult).filter_by(filteredSearchResultName = name).first()
    
    def verify_filtered_search_result(self, name):
        row = self.db_session.query(tPipeDB.FilteredSearchResult).filter_by(filteredSearchResultName = name).first()
        if row:
            return True
        else:
            return False
    

    def count_sources(self, assign_confidence_name, q_val_threshold):
        row = self.get_assign_confidence(assign_confidence_name)
        if row:
            print('tide search')
            print(row.tideSearch)
            print('tide index')
            print(row.tideSearch.tideIndex)
            print('filtered NetMHCs')
            print(row.tideSearch.tideIndex.filteredNetMHCs)
            print('peptide lists')
            print(row.tideSearch.tideIndex.peptidelists)
            print('target sets')
            print(row.tideSearch.tideIndex.targetsets)
            target_set_row = row.tideSearch.tideIndex.targetsets[0]
            q_val_column = 'tdc q-value'
            if row.estimation_method and len(row.estimation_method) > 0:
                q_val_column = row.estimation_method + ' q-value'
            handler = ReportGeneration.AssignConfidenceHandler(row, q_val_column, q_val_threshold, self.project_path)
            peptides = handler.getPeptides()
            
            return TargetSetSourceCount.count_sources(self.project_path, target_set_row, peptides)
    def add_targetset(self, netmhc_filter_names, peptide_list_names, target_set_name):
        #need to create lists of the form [(name, location)...]
        netmhc_filter_locations = []
        peptide_list_locations = []
        if netmhc_filter_names:
            for name in netmhc_filter_names:
                row  = self.db_session.query(tPipeDB.FilteredNetMHC).filter_by(FilteredNetMHCName = name).first()
                if row:
                    location = os.path.join(self.project_path, row.filtered_path)
                    netmhc_filter_locations.append((name, location))
                else:
                    raise NoSuchFilteredNetMHCError(name)
        if peptide_list_names:
            for name in peptide_list_names:
                row = self.db_session.query(tPipeDB.PeptideList).filter_by(peptideListName = name).first()
                if row:
                    location = os.path.join(self.project_path, row.PeptideListPath)
                    peptide_list_locations.append((name, location))
                else:
                    raise NoSuchPeptideListError(name)
        if self.db_session.query(tPipeDB.TargetSet).filter_by(TargetSetName = target_set_name).first():
            raise TargetSetNameMustBeUniqueError(target_set_name)
        
        output_folder = str(uuid.uuid4())
        while os.path.isdir(os.path.join(self.project_path, 'TargetSet', output_folder)) or os.path.isfile(os.path.join(self.project_path, 'TargetSet', output_folder)):
            output_folder = str(uuid.uuid4())
        os.mkdir(os.path.join(self.project_path, 'TargetSet', output_folder))
        output_fasta_location = os.path.join(self.project_path, 'TargetSet', output_folder, 'targets.fasta')
        output_json_location = os.path.join(self.project_path, 'TargetSet', output_folder, 'sources.json')

        source_id_map = create_target_set(netmhc_filter_locations, peptide_list_locations, output_fasta_location, output_json_location)
        target_set_row = tPipeDB.TargetSet(TargetSetFASTAPath = os.path.join('TargetSet', output_folder, 'targets.fasta'), PeptideSourceMapPath=os.path.join('TargetSet', output_folder, 'sources.json'), SourceIDMap=json.dumps(source_id_map), TargetSetName = target_set_name)
        self.db_session.add(target_set_row)
        self.db_session.commit()
    def verify_filtered_netMHC(self, name):
        if self.db_session.query(tPipeDB.FilteredNetMHC).filter_by(FilteredNetMHCName = name).first():
            return True
        else:
            return False
    def verify_target_set(self, name):
        if self.db_session.query(tPipeDB.TargetSet).filter_by(TargetSetName = name).first():
            return True
        else:
            return False
    def get_assign_confidence(self, assign_confidence_name):
        return self.db_session.query(tPipeDB.AssignConfidence).filter_by(AssignConfidenceName = assign_confidence_name).first()
    def get_percolator(self, percolator_name):
        return self.db_session.query(tPipeDB.Percolator).filter_by(PercolatorName = percolator_name).first()
    def list_assign_confidence(self, tide_search_name = None, estimation_method = None):
        filter_args = {}
        if tide_search_name:
            tide_search_row = self.db_session.query(tPipeDB.TideSearch).filter_by(TideSearchName = tide_search_name).first()
            if tide_search_row:
                filter_args['idTideSearch'] = tide_search_row.idTideSearch
            else:
                raise TideSearchRowDoesNotExistError(tide_search_name)
        if estimation_method:
            filter_args['estimation_method'] = estimation_method
        if len(filter_args.keys()) > 0:
            return self.db_session.query(tPipeDB.AssignConfidence).filter_by(**filter_args).all()
        else:
            return self.db_session.query(tPipeDB.AssignConfidence).all()
        
    def assign_confidence(self, tide_search_name, assign_confidence_runner, assign_confidence_name):
        tide_search_row = self.db_session.query(tPipeDB.TideSearch).filter_by(TideSearchName = tide_search_name).first()
        assign_confidence_row = self.db_session.query(tPipeDB.AssignConfidence).filter_by(AssignConfidenceName = assign_confidence_name).first()
        if tide_search_row and (assign_confidence_row is None):
            #run_assign_confidence_create_row(target_path, output_directory_tide, output_directory_db, assign_confidence_name)
            target_path = os.path.join(self.project_path, tide_search_row.targetPath)
            output_directory_name = str(uuid.uuid4().hex)
            while os.path.isdir(os.path.join(self.project_path, 'assign_confidence_results', output_directory_name)):
                output_directory_name = str(uuid.uuid4().hex)
            output_directory_tide = os.path.join(self.project_path, 'assign_confidence_results', output_directory_name)
            output_directory_db = os.path.join('assign_confidence_results', output_directory_name)
            new_row = assign_confidence_runner.run_assign_confidence_create_row(target_path, output_directory_tide, output_directory_db, assign_confidence_name, tide_search_row)
            self.db_session.add(new_row)
            self.db_session.commit()
        else:
            if tide_search_row is None:
                raise TideSearchRowDoesNotExistError(tide_search_name)
            if assign_confidence_row:
                raise AssignConfidenceNameMustBeUniqueError(assign_confidence_name)

    def percolator(self, tide_search_name, percolator_runner, percolator_name):
        tide_search_row = self.db_session.query(tPipeDB.TideSearch).filter_by(TideSearchName = tide_search_name).first()
        percolator_row = self.db_session.query(tPipeDB.Percolator).filter_by(PercolatorName = percolator_name).first()
        if tide_search_row and (percolator_row is None):
            target_path = os.path.join(self.project_path, tide_search_row.targetPath)
            output_directory_name = str(uuid.uuid4().hex)
            while os.path.isdir(os.path.join(self.project_path, 'percolator_results', output_directory_name)):
                output_directory_name = str(uuid.uuid4().hex)
            output_directory_tide = os.path.join(self.project_path, 'percolator_results', output_directory_name)
            output_directory_db = os.path.join('percolator_results', output_directory_name)
            new_row = percolator_runner.run_percolator_create_row(target_path, output_directory_tide, output_directory_db, percolator_name, tide_search_row)
            self.db_session.add(new_row)
            self.db_session.commit()
        else:
            if tide_search_row is None:
                raise TideSearchRowDoesNotExistError(tide_search_name)
            if percolator_row:
                raise PercolatorNameMustBeUniqueError(percolator_name)

    def list_tide_search(self, mgf_name = None, tide_index_name = None):
        """
        List the tide searches. You can specify an mgf name and/or tide index
        """
        filter_args = {}
        if mgf_name:
            mgf_row = self.db_session.query(tPipeDB.MGFfile).filter_by(MGFName = mgf_name).first()
            if mgf_row:
                filter_args['idMGF'] = mgf_row.idMGFfile
            else:
                raise MGFRowDoesNotExistError(mgf_name)
        if tide_index_name:
            tide_index_row = self.db_sesion.query(tPipeDB.TideIndex).filter_by(TideIndexName = tide_index_name).first()
            if tide_index_row:
                filter_args['idTideIndex'] = tide_index_row.idTideIndex
            else:
                raise NoSuchTideIndexError(tide_index_name)
        rows = []
        if len(filter_args.keys()) > 0:
            rows = self.db_session.query(tPipeDB.TideSearch).filter_by(**filter_args).all()
        else:
            rows = self.db_session.query(tPipeDB.TideSearch).all()
        return rows
        
    def run_tide_search(self, mgf_name, tide_index_name, tide_search_runner, tide_search_name, options):
        print('in tide search function')
        mgf_row = self.db_session.query(tPipeDB.MGFfile).filter_by(MGFName = mgf_name).first()
        tide_index_row = self.db_session.query(tPipeDB.TideIndex).filter_by(TideIndexName=tide_index_name).first()
        tide_search_row = self.db_session.query(tPipeDB.TideSearch).filter_by(TideSearchName=tide_search_name).first()
        if mgf_row and tide_index_row and (tide_search_row is None):
            directory_name = str(uuid.uuid4().hex)
            full_directory_path = os.path.join(self.project_path, 'tide_search_results', directory_name)
            while os.path.isfile(full_directory_path) or os.path.isdir(full_directory_path):
                directory_name = str(uuid.uuid4().hex)
                full_directory_path= os.path.join(self.project_path, 'tide_search_results', directory_name)
            row = tide_search_runner.run_search_create_row(mgf_row, tide_index_row, full_directory_path, os.path.join('tide_search_results', directory_name), options, self.project_path, tide_search_name)

            self.db_session.add(row)
            self.db_session.commit()
        else:
            if mgf_row is None:
                raise MGFRowDoesNotExistError(mgf_name)
            if tide_index_row is None:
                raise NoSuchTideIndexError(tide_index_name) 
            if tide_search_row:
                raise TideSearchNameMustBeUniqueError(tide_search_name)
    def add_mgf_file(self, path, name):
        row = self.db_session.query(tPipeDB.MGFfile).filter_by(MGFName = name).first()
        if row:
            raise MGFNameMustBeUniqueError(name)
        else:
            newpath = self.copy_file('MGF', path)
            mgf_record = tPipeDB.MGFfile(MGFName = name, MGFPath = newpath)
            self.db_session.add(mgf_record)
            self.db_session.commit()
            return mgf_record.idMGFfile    
    def get_tide_indices(self):
        rows = self.db_session.query(tPipeDB.TideIndex).all()
        indices = []
        for row in rows:
            index = {'name': row.TideIndexName, 'id': str(row.idTideIndex), 'path':row.TideIndexPath, 'peptide_lists':[], 'filteredNetMHCs':[], 'target_sets': []}
            for r in row.targetsets:
                index['target_sets'].append({'name': r.TargetSetName})
            for l in row.peptidelists:
                index['peptide_lists'].append({'name': l.peptideListName, 'length': str(l.length), 'fasta_name': l.fasta.Name})
            for n in row.filteredNetMHCs:
                netmhc = self.db_session.query(tPipeDB.NetMHC).filter_by(idNetMHC=n.idNetMHC).first()
                if netmhc:
                    peptide_list_row = self.db_session.query(tPipeDB.PeptideList).filter_by(idPeptideList=netmhc.peptidelistID).first()
                    hla_row = self.db_session.query(tPipeDB.HLA).filter_by(idHLA=netmhc.idHLA).first()
                    if peptide_list_row and hla_row:
                        index['filteredNetMHCs'].append({'hla': hla_row.HLAName, 'name': peptide_list_row.peptideListName, 'length': str(peptide_list_row.length), 'fasta_name': peptide_list_row.fasta.Name})
            indices.append(index)
        return indices

    def verify_peptide_list(self, peptide_list_name):
        row = self.db_session.query(tPipeDB.PeptideList).filter_by(peptideListName = peptide_list_name).first()
        if row is None:
            return False
        else:
            return True

    def verify_hla(self, hla):
        row = self.db_session.query(tPipeDB.HLA).filter_by(HLAName = hla).first()
        if row is None:
            return False
        else:
            return True

    def run_netmhc(self, peptide_list_name, hla, rank_cutoff, filtered_name, netmhcpan = False):
        idNetMHC, pep_score_path = self._run_netmhc(peptide_list_name, hla, netmhcpan)
        print('idNetMHC: ' + str(idNetMHC))
        
        row = self.db_session.query(tPipeDB.FilteredNetMHC).filter_by(idNetMHC = idNetMHC, RankCutoff = rank_cutoff).first()
        #to be clear, this means that 
        if row is None:
            file_name = str(uuid.uuid4())
            while os.path.isfile(os.path.join(self.project_path, 'FilteredNetMHC', file_name)) or os.path.isdir(os.path.join(self.project_path, 'FilteredNetMHC', file_name)):
                file_name = str(uuid.uuid4())
            print('current place: ' + os.getcwd())
            output_path = os.path.join(self.project_path, 'FilteredNetMHC', file_name)
            input_path = os.path.join(self.project_path, pep_score_path)
            with open(input_path, 'r') as f:
                with open(output_path, 'w') as g:
                    for line in f:
                        parts = line.split(',')
                        if len(parts) == 2:
                            peptide = parts[0].strip()
                            rank = float(parts[1])
                            if rank <= rank_cutoff:
                                g.write(peptide + '\n')
            
            
            filtered_row = tPipeDB.FilteredNetMHC(idNetMHC = idNetMHC, RankCutoff = rank_cutoff, FilteredNetMHCName = filtered_name, filtered_path = os.path.join('FilteredNetMHC', file_name))
            self.db_session.add(filtered_row)
            self.db_session.commit()
            
                
    def create_tide_index(self, set_type, set_name, tide_index_runner, tide_index_name):
        """
        tide_index_runner is an instance of the TideIndexRunner class
        """
        fasta_file_location = ''
        temp_files = []
        link_row = None
        if set_type == 'TargetSet':
            target_set_name = set_name
            row = self.db_session.query(tPipeDB.TargetSet).filter_by(TargetSetName = target_set_name).first()
            if row:
                link_row = row
                fasta_file_location = os.path.join(self.project_path, row.TargetSetFASTAPath)
            else:
                raise NoSuchTargetSetError(set_name)
        elif set_type == 'FilteredNetMHC':
            row = self.db_session.query(tPipeDB.FilteredNetMHC).filter_by(FilteredNetMHCName = set_name).first()
            if row:
                line_row = row
                temp_fasta = tempfile.NamedTemporaryFile(mode='w')
                subprocess.call(['bash_scripts/join_peptides_to_fasta.sh', os.path.join(self.project_path, row.filtered_path), temp_fasta.name])
                temp_files.append(temp_fasta)
                fasta_file_location = temp_fasta.name
            else:
                raise NoSuchFilteredNetMHCError(set_name)
        elif set_type == 'PeptideList':
            row = self.db_session.query(tPipeDB.PeptideList).filter_by(peptideListName = set_name).first()
            if row:
                link_row = row
                temp_fasta = tempfile.NamedTemporaryFile(mode='w')
                subprocess.call(['bash_scripts/join_peptides_to_fasta.sh', os.path.join(self.project_path, row.PeptideListpath), temp_fasta.name])
                temp_files.append(temp_fasta)
                fasta_file_location = temp_fasta.name
            else:
                raise NoSuchPeptideListError(set_name)
        else:
            assert(False)
        output_directory_name = str(uuid.uuid4().hex)
        output_directory_path = os.path.join(self.project_path, 'tide_indices', output_directory_name)
        while os.path.isfile(output_directory_path) or os.path.isdir(output_directory_path):
            output_directory_name = str(uuid.uuid4().hex)
            output_directory_path = os.path.join(self.project_path, 'tide_indices', output_directory_name)
        
        row = tide_index_runner.run_index_create_row(fasta_file_location, output_directory_path, os.path.join('tide_indices', output_directory_name), 'index')
        for x in temp_files:
            x.close()
        row.TideIndexName = tide_index_name
        if set_type == 'TargetSet':
            row.targetsets = [link_row]
        elif set_type == 'FilteredNetMHC':
            row.filteredNetMHCs = [link_row]
        elif set_type == 'PeptideList':
            row.peptidelists = [link_row]
        else:
            assert(False)
        self.db_session.add(row)
        self.db_session.commit()
        
    

    def generate_tide_index(self, peptide_list_names, netmhc_runs, tide_index_options):
        pass
    def add_peptide_list(self, name, length, fasta_name):
        fasta_row = self.db_session.query(tPipeDB.FASTA).filter_by(Name=fasta_name).first()
        if fasta_row is None:
            raise FASTAWithNameDoesNotExistError(fasta_name)
        print('length:')
        print(length)
        peptide_row = self.db_session.query(tPipeDB.PeptideList).filter_by(length = length, fasta = fasta_row).first()
        if peptide_row is None:
            fasta_filename = os.path.split(fasta_row.FASTAPath)[1]
            peptide_filename = fasta_filename + '_' + str(length) + '.txt'
            peptide_list_path = os.path.join('peptides', peptide_filename)
            if not os.path.isfile(os.path.join(self.project_path, peptide_list_path)):
                peptides = extract_peptides(os.path.join(self.project_path, fasta_row.FASTAPath), length)
                write_peptides(os.path.join(self.project_path, peptide_list_path), peptides)
            peptide_list = tPipeDB.PeptideList(peptideListName = name, length = length, fasta = fasta_row, PeptideListPath = peptide_list_path)
            self.db_session.add(peptide_list)
            self.db_session.commit()
    def _run_netmhc(self, peptide_list_name, hla_name, netmhcpan = False):
        """
        This first checks if there's already a in NetMHC for the given peptide list and HLA. If there is, then it just returns a tuple of the form: (idNetMHC, PeptideScorePath)
        
        If there isn't, then it runs NetMHC, inserts a row into the table, and returns (idNetMHC, PeptideScorePath)               
        """
        peptide_list_row = self.db_session.query(tPipeDB.PeptideList).filter_by(peptideListName=peptide_list_name).first()
        if peptide_list_row is None:
            raise NoSuchPeptideListError(peptide_list_name)
        hla_row = self.db_session.query(tPipeDB.HLA).filter_by(HLAName=hla_name).first()
        if hla_row is None:
            raise NoSuchHLAError(hla_name)
        netmhc_row = self.db_session.query(tPipeDB.NetMHC).filter_by(peptidelistID=peptide_list_row.idPeptideList, idHLA=hla_row.idHLA).first()
        if netmhc_row:
            return (netmhc_row.idNetMHC, netmhc_row.PeptideScorePath)
        else:
            netmhc_output_filename = str(uuid.uuid4().hex)
            while os.path.isfile(os.path.join(self.project_path, 'NetMHC', netmhc_output_filename)) or os.path.isfile(os.path.join(self.project_path, 'NetMHC', netmhc_output_filename, '-parsed')):
                netmhc_output_filename = str(uuid.uuid4().hex)
            call_netmhc(hla_name, os.path.join(self.project_path, peptide_list_row.PeptideListPath), os.path.join(self.project_path, 'NetMHC', netmhc_output_filename), netmhc_pan)
            parse_netmhc(os.path.join(self.project_path, 'NetMHC', netmhc_output_filename), os.path.join(self.project_path, 'NetMHC', netmhc_output_filename + '-parsed'))
            netmhc_row = tPipeDB.NetMHC(peptidelistID=peptide_list_row.idPeptideList, idHLA = hla_row.idHLA, NetMHCOutputPath=os.path.join('NetMHC', netmhc_output_filename), PeptideScorePath = os.path.join('NetMHC', netmhc_output_filename + '-parsed'))
            self.db_session.add(netmhc_row)
            self.db_session.commit()
            return (netmhc_row.idNetMHC, netmhc_row.PeptideScorePath)


    def list_peptide_lists(self):
        peptide_lists = []
        peptide_list_rows = self.db_session.query(tPipeDB.PeptideList).all()
        for row in peptide_list_rows:
            peptide_list = {'id': row.idPeptideList, 'name': row.peptideListName, 'FASTAName': row.fasta.Name, 'FASTAPath': row.fasta.FASTAPath, 'length': int(row.length), 'path': row.PeptideListPath}
            peptide_lists.append(peptide_list)
        return peptide_lists
    def list_files(self, folder):
        files_list = glob.glob(os.path.join(self.project_path, folder, '*'))
        return list(filter(lambda x: os.path.isfile(x), files_list))
    def list_fasta_files(self):
        return self.list_files('FASTA')
    def list_peptide_list_files(self):
        return self.list_files('peptides')
    def list_fasta_db(self):
        rows = self.db_session.query(tPipeDB.FASTA).all()
        fastas = []
        for row in rows:
            fasta = {'id': row.idFASTA, 'name': row.Name, 'comment': row.Comment, 'path': row.FASTAPath, 'peptide_lists': []}
            for pList in row.peptide_lists:
                fasta['peptide_lists'].append({'name': pList.peptideListName, 'length': pList.length})
            fastas.append(fasta)
        return fastas
    def list_mgf_db(self):
        rows = self.db_session.query(tPipeDB.MGFfile).all()        
        mgfs = []
        for row in rows:
            mgf = {'id': row.idMGFfile, 'name': row.MGFName, 'path': row.MGFPath}
            mgfs.append(mgf)
        return mgfs

    def add_species(self, species_name):
        species = tPipeDB.Species(SpeciesName = species_name)
        self.db_session.add(species)
    def validate_project_integrity(self, ignore_operation_lock = False):
        """
        Returns true if the project is valid. Otherwise it raises an error. That is:
        1) The lock file doesn't exist (operation_lock)
        2) All FASTA file paths in the FASTA table are found in the FASTA folder
        (and I'll add other criteria here as I expand the command set)
        3) All peptide list files are present
        """
        print('going to validate project integrity')
        print('current time: ' + str(datetime.now().time()))
        #if (not ignore_operation_lock) and os.path.isfile(os.path.join(self.project_path, 'operation_lock')):
        #    raise OperationsLockedError()
        print('going to check fasta rows')
        fasta_rows = self.db_session.query(tPipeDB.FASTA).all()
        for row in fasta_rows:
            path = row.FASTAPath
            if not os.path.isfile(os.path.join(self.project_path, path)):
                raise FASTAMissingError(row.idFASTA, row.Name, row.FASTAPath)
        print('going to check peptide list rows')
        peptide_list_rows = self.db_session.query(tPipeDB.PeptideList).all()
        for row in peptide_list_rows:
            path = row.PeptideListPath
            if not os.path.isfile(os.path.join(self.project_path, path)):
                raise PeptideListFileMissingError(row.idPeptideList, row.peptideListName, row.PeptideListPath)
        print('going to check mgf rows')
        mgf_rows = self.db_session.query(tPipeDB.MGFfile).all()
        for row in mgf_rows:
            path = row.MGFPath
            if not os.path.isfile(os.path.join(self.project_path, path)):
                raise MGFFileMissingError(row.idMGFfile, row.MGFName, row.MGFPath)
        print('done validating project integrity')
        print('current time: ' + str(datetime.now().time()))
        return True
    def lock_operations(self):
        pass
        #with open(os.path.join(self.project_path, 'operation_lock'), 'w') as f:
        #    pass
    def unlock_operations(self):
        pass
        #os.remove(os.path.join(self.project_path, 'operation_lock'))
        
    def mark_invalid(self):
        with open(os.path.join(self.project_path, 'project_invalid'), 'w') as f:
            pass
    def remove_invalid_mark(self):
        os.remove(os.path.join(self.project_path, 'project_invalid'))
    def begin_command_session(self, validate=True):
        """
        Validate project integrity, create operation lock
        """
        if validate:
            self.validate_project_integrity()
            current_place = os.getcwd()
            os.chdir(self.project_path)
            #shutil.make_archive('backup', 'gztar')
            #just copy the database.db file
            shutil.copyfile('database.db', 'database.db.backup')
            os.chdir(current_place)
            self.lock_operations()
    def end_command_session(self, validate=True):
        """
        Validate project integrity (ignoring the operation lock). If project does not have integrity, then rollback project.

        If it does have integrity, then remove operation lock, and remove backup"""
        
        self.command.executionSuccess = 1
        
        self.db_session.commit()
        if validate:
            try:
                self.validate_project_integrity(ignore_operation_lock = True)
            except Error as e:
                #rollback
                print('Doing the operations caused the project to become invalid; here is the error')
                print(sys.exc_info()[0])                
                sys.exit(1)
            else:
                self.unlock_operations()
                #os.remove(os.path.join(self.project_path, 'backup.tar.gz'))
    def copy_file(self, subfolder, path):
        files = self.list_files(subfolder)
        tails = [os.path.split(x)[1] for x in files]
        path_tail = os.path.split(path)[1]
        newpath= os.path.join(subfolder, path_tail)
        if path_tail in tails:
            max_version = 0
            """
            Let's say we add a FASTA file with the filename thing.fasta to our database 3 times.

            The first time, thing.fasta will be copied into the FASTA folder, and left with the filename "thing.fasta"
            The second time, a "-1" will be appended to the filename, to make "thing.fasta-1"
            The third time, a "-2" will be appended to the filename, to make "thing.fasta-2"
            """
            pattern = re.compile(re.escape(path_tail) + '-(?P<version>[0-9]*)')
            for tail in tails:
                match = pattern.match(tail)
                if match:
                    if len(match.group('version')) > 0:
                        version = int(match.group('version'))
                        if version > max_version:
                           max_version = version
            filename, extension = os.path.splitext(path_tail)
            
            newpath = os.path.join(subfolder, filename + '-' + str(max_version + 1) + extension)
        shutil.copy(path, os.path.join(self.project_path, newpath))
        return newpath
    def add_fasta_file(self, path, name, comment):
        """
        Steps:
        1) Validate that the file actually exists
        2) Make sure there isn't already a file with that name in the DB
        3) Validate that the file is actually a FASTA file
        4) Pick a name (the name in the filesystem, not the "name" column in the FASTA table) for the file, copy it over
        5) Add file to the database
        """
        if not os.path.isfile(path):
            raise FileDoesNotExistError(path)
        #step one done
        if len(self.db_session.query(tPipeDB.FASTA).filter_by(Name=name).all()) > 0:
            raise FASTAWithNameAlreadyExistsError(name)
        #step 2 done
        try:
            open_file = SeqIO.parse(path, 'fasta')
            for record in open_file:
                a = record.seq
        except:
            raise NotProperFASTAFileError(path)
        #step 3 done
        newpath = self.copy_file('FASTA', path)
        #did step 4
        fasta_record = tPipeDB.FASTA(Name = name, FASTAPath = newpath, Comment = comment)
        self.db_session.add(fasta_record)
        self.db_session.commit()
        return fasta_record.idFASTA
    def get_commands(self):
        commands = []
        for row in self.db_session.query(tPipeDB.Command):
            commands.append(row)
        return commands
    def get_species(self):
        species = []
        for row in self.db_session.query(tPipeDB.Species):
            hla = []
            for hla_row in row.hlas:
                hla.append(hla_row.HLAName)
            
            species.append({'id': row.idSpecies, 'name': row.SpeciesName, 'hla':hla  })
        return species

    def list_hla(self, species_name=None, species_id=None):
        if species_name:
            species_row = self.db_session.query(tPipeDB.Species).filter_by(SpeciesName=species_name).first()
            if species_row:
                species_id = species_row.idSpecies
            else:
                raise NoSuchSpeciesError(species_name)
        query = self.db_session.query(tPipeDB.HLA)
        if species_id:
            query = query.filter_by(species_id=species_id)
        rows = query.all()
        hlas = []
        for row in rows:
            hla = {'name': row.HLAName, 'id': str(row.idHLA)}
            if row.species:
                hla['species_id'] = str(row.species.idSpecies)
                hla['species_name'] = row.species.SpeciesName
            else:
                hla['species_id'] = 'None'
                hla['species_name'] = 'None'
            hlas.append(hla)
        return hlas
    def add_hla(self, hla_name):
        hla_rows = self.db_session.query(tPipeDB.HLA).filter_by(HLAName = hla_name).all()
        if len(hla_rows) > 0:
            raise HLAWithNameExistsError(hla_name)
        hla = tPipeDB.HLA(HLAName = hla_name)
        self.db_session.add(hla)
        self.db_session.commit()
        return hla.idHLA

        
        
        
    @staticmethod
    def createEmptyProject(project_path):
        if os.path.exists(project_path):
            raise ProjectPathAlreadyExistsError(project_path)
        else:
            os.mkdir(project_path)
            subfolders = ['FASTA', 'peptides', 'NetMHC', 'tide_indices', 'MGF', 'tide_search_results', 'percolator_results', 'misc', 'tide_param_files', 'assign_confidence_results', 'FilteredNetMHC', 'TargetSet']
            for subfolder in subfolders:
                os.mkdir(os.path.join(project_path, subfolder))
            return Project(project_path)



