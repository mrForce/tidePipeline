from AbstractEngine import AbstractEngine
import tempfile
import DB
import subprocess
import uuid
import os
import Runners
class TideEngine(AbstractEngine):
    def list_search(self, mgf_name = None, tide_index_name = None):
        """
        List the tide searches. You can specify an mgf name and/or tide index
        """
        filter_args = {}
        if mgf_name:
            mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
            if mgf_row:
                filter_args['idMGF'] = mgf_row.idMGFfile
            else:
                raise MGFRowDoesNotExistError(mgf_name)
        if tide_index_name:
            tide_index_row = self.db_sesion.query(DB.TideIndex).filter_by(TideIndexName = tide_index_name).first()
            if tide_index_row:
                filter_args['idTideIndex'] = tide_index_row.idTideIndex
            else:
                raise NoSuchTideIndexError(tide_index_name)
        rows = []
        if len(filter_args.keys()) > 0:
            rows = self.db_session.query(DB.TideSearch).filter_by(**filter_args).all()
        else:
            rows = self.db_session.query(DB.TideSearch).all()
        return rows
    """
    peptide_identifier is either 'assign_confidence' or 'percolator'. 
    """
    def multistep_search(self, mgf_name, tide_index_names, search_options, multistep_search_name, filtered_search_result_name, fdr, percolator_param_file, postprocess_object):
        mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
        multistep_search_row = self.db_session.query(DB.TideIterativeRun).filter_by(TideIterativeRunName = multistep_search_name).first()
        filtered_search_result_row = self.db_session.query(DB.FilteredSearchResult).filter_by(filteredSearchResultName = filtered_search_result_name).first()
        crux_location = self.executables['crux']
        peptide_identifier = 'percolator'
        if mgf_row and (multistep_search_row is None) and (filtered_search_result_row is None):
            #make sure the tide indices exist
            for name in tide_index_names:
                tide_index_row = self.db_session.query(DB.TideIndex).filter_by(TideIndexName = name).first()
                if tide_index_row is None:
                    raise NoSuchTideIndexError(name)
            """
            The name of each TideSearch row should be multistep_search_name + '_' + tide_index_name. 
            
            For each TideSearch, there will be a corresponding Percolator row. The name of this row should be multistep_search_name + '_' + tide_index_name + '_percolator'. 

            Each intermediate MGF file will be named multistep_search_name + '_' tide_index_name + '_mgf'

            We need to make sure each of these rows doesn't exist!
            """
            first_index = True
            for name in tide_index_names:
                new_search_name = multistep_search_name + '_' + name
                new_tide_search_row = self.db_session.query(DB.TideSearch).filter_by(TideSearchName = new_search_name).first()
                if not (new_tide_search_row is None):
                    raise TideSearchNameMustBeUniqueError(new_search_name)
                new_percolator_name = new_search_name + '_' + peptide_identifier
                new_percolator_row = self.db_session.query(DB.Percolator).filter_by(PercolatorName = new_percolator_name).first()
                if not (new_percolator_row is None):
                    raise PercolatorNameMustBeUniqueError(new_percolator_name)
                if not first_index:
                    new_mgf_name = multistep_search_name + '_' + name + '_mgf'
                    new_mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = new_mgf_name).first()
                    if not (new_mgf_row is None):
                        raise MGFNameMustBeUniqueError(new_mgf_name)
                else:
                     first_index = False   
                    

            """
            We're clear to start running the searches. We'll run the search on the mgf passed to us, then run Percolator, then extract the PSMs using PercolatorHandler from ReportGeneration. We'll extract the matched spectra from the MGF, creating a new MGF, and search it against the next tide index
            """
            first_index = True
            new_mgf_name = mgf_name
            for index_name in tide_index_names:
                if not first_index:
                    new_mgf_name = multistep_search_name + '_' + index_name + '_mgf'
                else:
                    first_index = False
                search_name = multistep_search_name + '_' + index_name
                percolator_name = search_name + '_' + peptide_identifier
                search_runner = Runners.TideSearchRunner(search_options, crux_location)
                self.run_search(new_mgf_name, index_name, search_runner, search_name, search_options)
                #We ran the search, so now we need to call Percolator
                postprocessing_object.percolator(search_name, Runners.PercolatorRunner(crux_location, percolator_param_file), percolator_name)
                #open up the Percolator results using PercolatorHandler
                percolator_handler = ReportGeneration.PercolatorHandler(percolator_name, fdr, self.project_path, self.db_session, crux_location)
                psms = percolator_handler.get_psms()
                #parse the MGF file, and remove the scans corresponding to discovered peptides
    def run_search(self, mgf_name, tide_index_name, tide_search_runner, tide_search_name, options):
        print('in tide search function')
        mgf_row = self.db_session.query(DB.MGFfile).filter_by(MGFName = mgf_name).first()
        tide_index_row = self.db_session.query(DB.TideIndex).filter_by(TideIndexName=tide_index_name).first()
        tide_search_row = self.db_session.query(DB.TideSearch).filter_by(SearchName=tide_search_name).first()
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
    def list_indices(self):
        rows = self.db_session.query(DB.TideIndex).all()
        indices = []
        for row in rows:
            index = {'name': row.TideIndexName, 'id': str(row.idIndex), 'path':row.TideIndexPath, 'peptide_lists':[], 'filteredNetMHCs':[], 'target_sets': []}
            for r in row.targetsets:
                index['target_sets'].append({'name': r.TargetSetName})
            for l in row.peptidelists:
                index['peptide_lists'].append({'name': l.peptideListName, 'length': str(l.length), 'fasta_name': l.fasta.Name})
            for n in row.filteredNetMHCs:
                netmhc = self.db_session.query(DB.NetMHC).filter_by(idNetMHC=n.idNetMHC).first()
                if netmhc:
                    peptide_list_row = self.db_session.query(DB.PeptideList).filter_by(idPeptideList=netmhc.peptidelistID).first()
                    hla_row = self.db_session.query(DB.HLA).filter_by(idHLA=netmhc.idHLA).first()
                    if peptide_list_row and hla_row:
                        index['filteredNetMHCs'].append({'hla': hla_row.HLAName, 'name': peptide_list_row.peptideListName, 'length': str(peptide_list_row.length), 'fasta_name': peptide_list_row.fasta.Name})
            indices.append(index)
        return indices
    


    def create_index(self, set_type, set_name, tide_index_runner, tide_index_name):
        """
        tide_index_runner is an instance of the TideIndexRunner class
        """
        fasta_file_location, link_row, temp_files  = self.create_fasta_for_indexing(set_type, set_name)
        output_directory_name = str(uuid.uuid4().hex)
        output_directory_path = os.path.join(self.project_path, 'tide_indices', output_directory_name)
        while os.path.isfile(output_directory_path) or os.path.isdir(output_directory_path):
            output_directory_name = str(uuid.uuid4().hex)
            output_directory_path = os.path.join(self.project_path, 'tide_indices', output_directory_name)
        
        row = tide_index_runner.run_index_create_row(fasta_file_location, output_directory_path, os.path.join('tide_indices', output_directory_name), 'index')
        for x in temp_files:
            x.close()
        row.TideIndexName = tide_index_name
        print('link row')
        print(link_row)
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
