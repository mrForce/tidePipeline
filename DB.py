from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, create_engine, Float, BLOB, DateTime, Boolean
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm.session import object_session
import datetime
from Parsers import MaxQuantPeptidesParser
import shutil
from abc import ABCMeta, abstractmethod, ABC
import os
import Errors
import fileFunctions
#BaseTable = declarative_base(metaclass=ABCMeta)

class CustomMetaClass(DeclarativeMeta, ABCMeta):
    pass

BaseTable = declarative_base(metaclass=CustomMetaClass)

class AbstractPeptideCollection(ABC):
    #get_peptides should return a set of peptides. Each peptide is a string.
    @abstractmethod
    def get_peptides(self, project_path):
        pass


def delete_objects(root, files, directories = []):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        print('removing file: ' + file_path)
    
        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            raise Errors.FileMarkedForDeletionDoesNotExistError(file_path)
        

    for dir_name in directories:
        dir_path = os.path.join(root, dir_name)
        print('removing directory: ' + dir_path)
        """
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
        else:
            raise Errors.DirectoryMarkedForDeletionDoesNotExistError(dir_path)
        """

def extract_peptides_from_peptides_format(path):
    peptides = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) > 1:
                peptides.append(line)
    return peptides



indexbase_netmhc_decoys = Table('indexbase_netmhc_decoys', BaseTable.metadata, Column('indexbase_id', ForeignKey('IndexBase.idIndex'), primary_key=True), Column('netmhc_id', ForeignKey('NetMHC.idNetMHC'), primary_key=True))
indexbase_contaminantSet = Table('indexbase_contaminantSet', BaseTable.metadata, Column('indexbase_id', ForeignKey('IndexBase.idIndex'), primary_key=True), Column('contaminantset_id', ForeignKey('ContaminantSet.idContaminantSet'), primary_key=True))

maxquantsearch_contaminantSet = Table('maxquantsearch_contaminantSet', BaseTable.metadata, Column('maxquantsearch_id', ForeignKey('MaxQuantSearch.idSearch'), primary_key=True), Column('contaminantset_id', ForeignKey('ContaminantSet.idContaminantSet'), primary_key=True))


class ContaminantSet(BaseTable, AbstractPeptideCollection):
    __tablename__ = "ContaminantSet"
    idContaminantSet = Column('idContaminantSet', Integer, primary_key=True)
    contaminantSetName = Column('contaminantSetName', String, unique=True)
    fasta_file = Column('fasta_file', String)
    peptide_file = Column('peptide_file', String, nullable=False)
    _lengths = Column(String, default='')
    indices = relationship('IndexBase', secondary = indexbase_contaminantSet, back_populates='contaminants')
    maxquantsearches = relationship('MaxQuantSearch', secondary = maxquantsearch_contaminantSet, back_populates='contaminants')
    """
    This assumes we already imported the FASTA file into the project, and peptides_path is where within the project we are supposed to put the peptides
    """
    def __init__(self, project_path, path, peptides_path, lengths, name, protein_format):
        full_path = os.path.join(project_path, path)
        if protein_format == 'FASTA':
            self.fasta_file = path
            self.peptide_file = peptides_path
        elif protein_format == 'peptides':
            self.peptide_file = path
            peptides_path = path
        self.contaminantSetName = name
        peptides = []
        if lengths:
            
            self.lengths = lengths
            for length in lengths:
                peptides_of_length = fileFunctions.extract_peptides(full_path, length, file_format = protein_format)
                peptides.extend(peptides_of_length)
        else:
            peptides = fileFunctions.extract_peptides(full_path, None, file_format = protein_format)
        uniq_peptides = list(set(peptides))
        with open(os.path.join(project_path, peptides_path), 'w') as f:
            for peptide in uniq_peptides:
                f.write(peptide + '\n')
        
            
    @property
    def lengths(self):
        return [int(x) for x in self._lengths]
    @lengths.setter
    def lengths(self, value):

        if isinstance(value, list):
            self._lengths = ','.join([str(x) for x in value])
        elif isinstance(value, int):
            self._lengths += (',%i' % value)
        

    def get_peptides(self, project_path):
        peptides = []
        lengths = self.lengths
        with open(self.peptide_file, 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) in lengths:
                    peptides.append(line)
        return peptides
                    
"""
This links an iterative search with the MGF files it created
"""        

class IterativeRunMGFAssociation(BaseTable):
    __tablename__ = 'IterativeRunMGFAssociation'
    iterativerun_id = Column('iterativerun_id', ForeignKey('IterativeSearchRun.idIterativeSearchRun'), primary_key=True)
    mgf_id = Column('mgf_id', ForeignKey('MGFfile.idMGFfile'), primary_key=True)
    mgf = relationship('MGFfile', cascade='all,delete')
    iterativerun = relationship('IterativeSearchRun')
class IterativeRunSearchAssociation(BaseTable):
    __tablename__ = 'IterativeRunSearchAssociation'
    iterativerun_id = Column('iterativerun_id', ForeignKey('IterativeSearchRun.idIterativeSearchRun'), primary_key=True)
    search_id = Column('search_id', ForeignKey('SearchBase.idSearch'), primary_key=True)
    search = relationship('SearchBase', cascade='all,delete')
    iterativerun = relationship('IterativeSearchRun')







        
tideindex_filteredNetMHC = Table('tideindex_filteredNetMHC', BaseTable.metadata, Column('tideindex_id', ForeignKey('TideIndex.idIndex'), primary_key=True), Column('filteredNetMHC_id', ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))

msgfplus_index_filteredNetMHC = Table('msgfplus_index_filteredNetMHC', BaseTable.metadata, Column('msgfplus_index_id', ForeignKey('MSGFPlusIndex.idIndex'), primary_key=True), Column('filteredNetMHC_id', ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))

maxquant_search_filteredNetMHC = Table('maxquant_search_filteredNetMHC', BaseTable.metadata, Column('maxquant_search_id', ForeignKey('MaxQuantSearch.idSearch'), primary_key=True), Column('filteredNetMHC_id', ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))

tideindex_peptidelists = Table('tideindex_peptidelists', BaseTable.metadata, Column('tideindex_id', ForeignKey('TideIndex.idIndex'), primary_key=True), Column('peptidelist_id', ForeignKey('PeptideList.idPeptideList'), primary_key=True))


msgfplus_index_peptidelists = Table('msgfplus_index_peptidelists', BaseTable.metadata, Column('msgfplus_index_id', ForeignKey('MSGFPlusIndex.idIndex'), primary_key=True), Column('peptidelist_id', ForeignKey('PeptideList.idPeptideList'), primary_key=True))

maxquant_search_peptidelists = Table('maxquant_search_peptidelists', BaseTable.metadata, Column('maxquant_search_id', ForeignKey('MaxQuantSearch.idSearch'), primary_key=True), Column('peptidelist_id', ForeignKey('PeptideList.idPeptideList'), primary_key=True))


"""
Need to add the following 3 tables in database revision 8d70dec8ab88
"""
tideindex_targetset = Table('tideindex_targetset', BaseTable.metadata, Column('tideindex_id', ForeignKey('TideIndex.idIndex'), primary_key = True), Column('targetset_id', ForeignKey('TargetSet.idTargetSet'), primary_key=True))

maxquant_search_targetset = Table('maxquant_search_targetset', BaseTable.metadata, Column('maxquant_search_id', ForeignKey('MaxQuantSearch.idSearch'), primary_key = True), Column('targetset_id', ForeignKey('TargetSet.idTargetSet'), primary_key=True))

msgfplus_index_targetset = Table('msgfplus_index_targetset', BaseTable.metadata, Column('msgfplus_index_id', ForeignKey('MSGFPlusIndex.idIndex'), primary_key = True), Column('targetset_id', ForeignKey('TargetSet.idTargetSet'), primary_key=True))

msgfplus_index_fasta = Table('msgfplus_index_fasta', BaseTable.metadata, Column('msgfplus_index_id', ForeignKey('MSGFPlusIndex.idIndex'), primary_key = True), Column('fasta_id', ForeignKey('FASTA.idFASTA'), primary_key=True))



targetset_filteredNetMHC = Table('targetset_filteredNetMHC', BaseTable.metadata, Column('targetset_id', ForeignKey('TargetSet.idTargetSet'), primary_key = True), Column('filteredNetMHC_id', ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))
targetset_peptidelists = Table('targetset_peptidelists', BaseTable.metadata, Column('targetset_id', ForeignKey('TargetSet.idTargetSet'), primary_key = True), Column('peptideList_id', ForeignKey('PeptideList.idPeptideList'), primary_key=True))


 


class IterativeFilteredSearchAssociation(BaseTable):
    __tablename__ = 'IterativeFilteredSearchAssociation'
    iterative_id = Column(Integer, ForeignKey('IterativeSearchRun.idIterativeSearchRun'), primary_key=True)
    filteredsearch_id = Column(Integer, ForeignKey('FilteredSearchResult.idFilteredSearchResult'), primary_key=True)
    step = Column('step', Integer)
    filteredsearch_result = relationship('FilteredSearchResult', cascade='all,delete')

    

    
class IterativeSearchRun(BaseTable):
    __tablename__ = 'IterativeSearchRun'
    idIterativeSearchRun = Column('idIterativeSearchRun', Integer, primary_key=True)
    IterativeSearchRunName = Column('IterativeSearchRunName', String, unique=True)
    searchType = Column(String(50))
    IterativeFilteredSearchAssociations = relationship('IterativeFilteredSearchAssociation', cascade='all,delete')
    IterativeRunMGFAssociations = relationship('IterativeRunMGFAssociation', cascade='all,delete')
    
    __mapper_args__ = {
        'polymorphic_identity': 'iterativesearch',
        'polymorphic_on': searchType
    }
    def identifier(self):
        return self.IterativeSearchRunName
    def get_contaminant_sets(self):
        session = object_session(self)
        rows = session.query(IterativeRunSearchAssociation).filter_by(iterativerun_id = self.idIterativeSearchRun).all()
        contaminant_sets = list()
        for row in rows:
            contaminant_sets.extend(row.get_contaminant_sets())
        return list(set(contaminant_sets))


class MSGFPlusIterativeRun(IterativeSearchRun, AbstractPeptideCollection):
    __tablename__ = 'MSGFPlusIterativeRun'
    idIterativeSearchRun = Column(Integer, ForeignKey('IterativeSearchRun.idIterativeSearchRun'), primary_key=True, autoincrement=True)
#    MSGFPlusIterativeRunName = Column('MSGFPlusIterativeRunName', String, unique=True)
    fdr = Column('fdr', String)
    num_steps = Column('num_steps', Integer)
    idMGF = Column('idMGF', Integer, ForeignKey('MGFfile.idMGFfile'))
    mgf = relationship('MGFfile')
    __mapper_args = {
        'polymorphic_identity': 'msgf'
    }

    def get_peptides(self, project_path):
        associations = self.MSGFPlusIterativeFilteredSearchAssociations
        assert(len(associations) == self.num_steps)
        peptide_set_list = []
        for row in associations:
            peptide_set_list.append(row.filteredsearch_result.get_peptides(project_path))
        return set([item for subset in peptide_set_list for item in subset])



        
class TideIterativeRun(IterativeSearchRun, AbstractPeptideCollection):
    __tablename__ = 'TideIterativeRun'
    idIterativeSearchRun = Column(Integer, ForeignKey('IterativeSearchRun.idIterativeSearchRun'), primary_key=True, autoincrement=True)
    fdr = Column('fdr', String)
    PeptideIdentifierName = Column('PeptideIdentifierName', String)
    num_steps = Column('num_steps', Integer)
    
    """
    mgf is the mgf we started with
    """
    idMGF = Column('idMGF', Integer, ForeignKey('MGFfile.idMGFfile'))
    mgf = relationship('MGFfile')
    __mapper_args__ = {
        'polymorphic_identity': 'tide'
    }


    def get_peptides(self, project_path):
        associations = self.TideIterativeFilteredSearchAssociations
        assert(len(associations) == self.num_steps)
        peptide_set_list = []
        for row in associations:
            peptide_set_list.append(row.filteredsearch_result.get_peptides(project_path))
        return set([item for subset in peptide_set_list for item in subset])

            
    
class TargetSet(BaseTable, AbstractPeptideCollection):
    __tablename__ = 'TargetSet'
    idTargetSet = Column('idTargetSet', Integer, primary_key = True)
    TargetSetFASTAPath = Column('TargetSetFASTAPath', String, unique=True)
    PeptideSourceMapPath = Column('PeptideSourceMapPath', String)
    SourceIDMap = Column('SourceIDMap', String)
    TargetSetName = Column('TargetSetName', String, unique=True)
    filteredNetMHCs = relationship('FilteredNetMHC', secondary=targetset_filteredNetMHC, back_populates='targetsets')
    peptidelists = relationship('PeptideList', secondary=targetset_peptidelists, back_populates='targetsets')
    tideindices = relationship('TideIndex', secondary=tideindex_targetset, back_populates='targetsets')
    msgfplusindices = relationship('MSGFPlusIndex', secondary=msgfplus_index_targetset, back_populates='targetsets')
    maxquantsearches = relationship('MaxQuantSearch', secondary=maxquant_search_targetset, back_populates='targetsets')
    def remove_files(self, project_root):
        delete_objects(project_root, [self.TargetSetFASTAPath, self.PeptideSourceMapPath])
            
    def identifier(self):
        return self.TargetSetName
    def get_peptides(self, project_path):
        fasta_location = os.path.join(project_path, self.TargetSetFASTAPath)
        with open(fasta_location, 'r') as f:
            peptides = set()
            for line in f:
                stripped_line = line.strip()
                if len(stripped_line) >= 1 and ('>' not in stripped_line):
                    peptides.add(stripped_line)
        return peptides
class HLA(BaseTable):
    __tablename__ = 'HLA'
    idHLA = Column('idHLA', Integer, primary_key = True)
    HLAName = Column('HLAName', String, unique=True)
    netmhcs = relationship('NetMHC', back_populates='hla')
    def identifier(self):
        return self.HLAName


class MGFfile(BaseTable):
    __tablename__ = 'MGFfile'
    idMGFfile = Column('idMGFfile', Integer, primary_key=True)
    MGFName = Column('MGFName', String, unique=True)
    MGFPath = Column('MGFPath', String)
    partOfIterativeSearch = Column('partOfIterativeSearch', Boolean, default=False)
    def __repr__(self):
        return self.MGFName
    def identifier(self):
        return self.MGFName
    def remove_files(self, project_root):
        delete_objects(project_root, [self.MGFPath])
    def __prepare_deletion__(self, project_root):
        self.remove_files(project_root)

    """
    If partOfIterativeSearch is true, then this was created by an iterative search. Check that it is linked to at least one iterative search
    """
    def is_valid(self):
        if self.partOfIterativeSearch:
            session = object_session(self)
            rows = session.query(IterativeRunMGFAssociation).filter_by(mgf_id = self.idMGFfile).all()
            if rows:
                return True
            else:
                return False
        return True
class RAWfile(BaseTable):
    __tablename__ = 'RAWfile'
    idRAWfile = Column('idRAWfile', Integer, primary_key=True)
    RAWName = Column('RAWName', String, unique=True)
    RAWPath = Column('RAWPath', String)
    def __repr__(self):
        return 'RAW File found at: ' + self.RAWPath
    def identifier(self):
        return self.RAWName
    def remove_files(self, project_root):
        delete_objects(project_root, [self.RAWPath])

class FASTA(BaseTable):
    __tablename__ = 'FASTA'
    idFASTA = Column('idFASTA', Integer, primary_key=True)
    Name = Column('Name', String, unique=True)
    FASTAPath = Column('FASTAPath',  String, unique=True)
    Comment = Column('Comment', String)
    peptide_lists = relationship('PeptideList', back_populates='fasta')
    msgfplusindices = relationship('MSGFPlusIndex', secondary=msgfplus_index_fasta, back_populates='fasta')
    def __repr__(self):
        return 'FASTA File found at: ' + self.FASTAPath + ' with comment: ' + self.Comment
    def identifier(self):
        return self.Name

    def remove_files(self, project_root):
        delete_objects(project_root, [self.FASTAPath])

class MaxQuantParameterFile(BaseTable):
    __tablename__ = 'MaxQuantParameterFile'
    idMaxQuantParameterFile = Column('idMaxQuantParameterFile', Integer, primary_key=True)
    Name = Column('Name', String, unique=True, nullable=False)
    Path = Column('Path', String, nullable=False)
    Comment = Column('Comment', String)
    def __repr__(self):
        if self.Comment is None:
            return 'MaxQuant parameter file found at: ' + self.Path
        else:
            return 'MaxQuant parameter file found at: ' + self.Path + ' with comment: ' + self.Comment
    def identifier(self):
        return self.Name

    def remove_files(self, project_root):
        delete_objects(project_root, [self.Path])

class TideSearchParameterFile(BaseTable):
    __tablename__ = 'TideSearchParameterFile'
    idTideSearchParameterFile = Column('idTideSearchParameterFile', Integer, primary_key=True)
    Name = Column('Name', String, unique=True, nullable=False)
    Path = Column('Path', String, unique=True, nullable=False)
    Comment = Column('Comment', String)
    def __repr__(self):
        if self.Comment is None:
            return 'Tide Search parameter file found at: ' + self.Path
        else:
            return 'Tide Search parameter file found at: ' + self.Path + ' with comment: ' + self.Comment
    def identifier(self):
        return self.Name
    def remove_files(self, project_root):
        delete_objects(project_root, [self.Path])

class TideIndexParameterFile(BaseTable):
    __tablename__ = 'TideIndexParameterFile'
    idTideIndexParameterFile = Column('idTideIndexParameterFile', Integer, primary_key=True)
    Name = Column('Name', String, unique=True, nullable=False)
    Path = Column('Path', String, unique=True, nullable=False)
    Comment = Column('Comment', String)
    def __repr__(self):
        if self.Comment is None:
            return 'Tide Index parameter file found at: ' + self.Path
        else:
            return 'Tide Index parameter file found at: ' + self.Path + ' with comment: ' + self.Comment

    def identifier(self):
        return self.Name
    def remove_files(self, project_root):
        delete_objects(project_root, [self.Path])

class AssignConfidenceParameterFile(BaseTable):
    __tablename__ = 'AssignConfidenceParameterFile'
    idAssignConfidenceParameterFile = Column('idAssignConfidenceParameterFile', Integer, primary_key=True)
    Name = Column('Name', String, unique=True, nullable=False)
    Path = Column('Path', String, unique=True, nullable=False)
    Comment = Column('Comment', String)
    def __repr__(self):
        if self.Comment is None:
            return 'Assign Confidence parameter file found at: ' + self.Path
        else:
            return 'Assign Confidence parameter file found at: ' + self.Path + ' with comment: ' + self.Comment
    def identifier(self):
        return self.Name

    def remove_files(self, project_root):
        delete_objects(project_root, [self.Path])

class PercolatorParameterFile(BaseTable):
    __tablename__ = 'PercolatorParameterFile'
    idPercolatorParameterFile = Column('idPercolatorParameterFile', Integer, primary_key=True)
    Name = Column('Name', String, unique=True, nullable=False)
    Path = Column('Path', String, unique=True, nullable=False)
    Comment = Column('Comment', String)
    def __repr__(self):
        if self.Comment is None:
            return 'Percolator parameter file found at: ' + self.Path
        else:
            return 'Percolator parameter file found at: ' + self.Path + ' with comment: ' + self.Comment
    def identifier(self):
        return self.Name
    def remove_files(self, project_root):
        delete_objects(project_root, [self.Path])
        
class PeptideList(BaseTable, AbstractPeptideCollection):
    __tablename__ = 'PeptideList'
    idPeptideList = Column('idPeptideList', Integer, primary_key=True)
    peptideListName = Column('peptideListName', String, unique=True)
    idFASTA = Column(Integer, ForeignKey('FASTA.idFASTA'))
    fasta = relationship('FASTA', back_populates='peptide_lists')
    PeptideListPath = Column('PeptideListPath', String)
    #Just a string of integers seperated by spaces. 
    length = Column('length', Integer)
    tideindices = relationship('TideIndex', secondary=tideindex_peptidelists, back_populates='peptidelists')
    targetsets = relationship('TargetSet', secondary=targetset_peptidelists, back_populates='peptidelists')
    msgfplusindices = relationship('MSGFPlusIndex', secondary=msgfplus_index_peptidelists, back_populates='peptidelists')
    maxquantsearches = relationship('MaxQuantSearch', secondary=maxquant_search_peptidelists, back_populates='peptidelists')
    def remove_files(self, project_root):
        delete_objects(project_root, [self.PeptideListPath])

    def __repr__(self):
        return 'Peptide List can be found at: ' + self.PeptideListPath
    def identifier(self):
        return self.peptideListName
    def get_peptides(self, project_path):
        peptides = set()
        with open(os.path.join(project_path, self.PeptideListPath), 'r') as f:
            for line in f:
                stripped_line = line.strip()
                if len(stripped_line) >= 1:
                    peptides.add(stripped_line)
        return peptides

class NetMHC(BaseTable):
    __tablename__ = 'NetMHC'
    idNetMHC = Column('idNetMHC', Integer, primary_key = True)
    peptidelistID = Column(Integer, ForeignKey('PeptideList.idPeptideList'))
    idHLA = Column(Integer, ForeignKey('HLA.idHLA'))
    Name = Column('Name', String, unique=True)
    hla = relationship('HLA', back_populates='netmhcs')
    #Raw output of NetMHC
    NetMHCOutputPath = Column('NetMHCOutputPath', String)
    #a TXT file, each line is a peptide, then a comma, then the rank
    #used to be PeptideScorePath
    PeptideAffinityPath = Column('PeptideAffinityPath', String)
    PeptideRankPath = Column('PeptideRankPath', String)
    peptidelist = relationship('PeptideList', cascade='all,delete')
    indexbase_decoys = relationship('IndexBase', secondary=indexbase_netmhc_decoys, back_populates='netmhc_decoys')
    def length(self):
        return self.peptidelist.length
    def remove_files(self, project_root):
        delete_objects(project_root, [self.NetMHCOutputPath, self.PeptideAffinityPath, self.PeptideRankPath])
    
class FilteredNetMHC(BaseTable, AbstractPeptideCollection):
    __abstract__ = False
    __tablename__ = 'FilteredNetMHC'
    idFilteredNetMHC = Column('idFilteredNetMHC', Integer, primary_key=True)
    idNetMHC = Column(Integer, ForeignKey('NetMHC.idNetMHC'))
    filtered_path = Column('filtered_path', String)
    FilteredNetMHCName = Column('FilteredNetMHCName', String)
    RankCutoff = Column('RankCutoff', Float)
    tideindices = relationship('TideIndex', secondary=tideindex_filteredNetMHC, back_populates='filteredNetMHCs')
    targetsets = relationship('TargetSet', secondary=targetset_filteredNetMHC, back_populates='filteredNetMHCs')
    msgfplusindices = relationship('MSGFPlusIndex', secondary=msgfplus_index_filteredNetMHC, back_populates='filteredNetMHCs')
    maxquantsearches = relationship('MaxQuantSearch', secondary=maxquant_search_filteredNetMHC, back_populates='filteredNetMHCs')
    netmhc = relationship('NetMHC')
    def remove_files(self, project_root):
        delete_objects(project_root, [self.filtered_path])
    def get_peptides(self, project_path):
        peptides = set()
        with open(os.path.join(project_path, self.filtered_path), 'r') as f:
            for line in f:
                stripped_line = line.strip()
                if len(stripped_line) >= 1:
                    peptides.add(stripped_line)
        return peptides


    def identifier(self):
        return self.FilteredNetMHCName
        
class IndexBase(BaseTable):
    __tablename__ = 'IndexBase'
    idIndex = Column('idIndex', Integer, primary_key=True)
    indexType = Column(String(50))
    customDecoys = Column('customDecoys', Integer, default=0)
    netmhc_decoys = relationship('NetMHC', secondary=indexbase_netmhc_decoys, back_populates='indexbase_decoys')
    contaminants = relationship('ContaminantSet', secondary = indexbase_contaminantSet, back_populates='indices')
    __mapper_args__ = {
        'polymorphic_identity': 'indexbase',
        'polymorphic_on': indexType
    }

    def get_contaminant_sets(self):
        return self.contaminants
class TideIndex(IndexBase):
    __tablename__ = 'TideIndex'
    idIndex = Column(Integer, ForeignKey('IndexBase.idIndex'), primary_key=True)
    idParameterFile = Column('idParameterFile', Integer, ForeignKey('TideIndexParameterFile.idTideIndexParameterFile'))
    parameterFile = relationship('TideIndexParameterFile')
    #the name of the index is given by the user
    TideIndexName = Column('TideIndexName', String, unique=True)
    TideIndexPath = Column('TideIndexPath', String)
    clip_nterm_methionine = Column(Integer)
    isotopic_mass = Column(String)
    max_length = Column(Integer)
    #max and min mass are really floats -- but I'm not sure about the precision of Sqlite, so I'll just store them as strings
    max_mass = Column(String)
    min_length = Column(Integer)
    min_mass = Column(String)
    cterm_peptide_mods_spec = Column(String)
    max_mods = Column(Integer)
    min_mods = Column(Integer)
    mod_precision = Column(Integer)
    mods_spec = Column(String)
    nterm_peptide_mods_spec = Column(String)
    allow_dups = Column(Integer)
    decoy_format = Column(String)
    decoy_generator = Column(String)
    keep_terminal_aminos = Column(String)
    seed = Column(String)
    custom_enzyme = Column(String)
    digestion = Column(String)
    enzyme = Column(String)
    missing_cleavages = Column(Integer)
    filteredNetMHCs = relationship('FilteredNetMHC', secondary = tideindex_filteredNetMHC, back_populates = 'tideindices')
    peptidelists = relationship('PeptideList', secondary= tideindex_peptidelists, back_populates = 'tideindices')
    targetsets = relationship('TargetSet', secondary=tideindex_targetset, back_populates='tideindices')
    searches = relationship('TideSearch', back_populates = 'tideindex', cascade='all,delete')
    __mapper_args__ = {
        'polymorphic_identity': 'tideindex',
    }
    def remove_files(self, project_root):
        delete_objects(project_root,[],  [os.path.dirname(self.TideIndexPath)])
    def identifier(self):
        return self.TideIndexName
    def is_valid(self):
        """
        If this is used in any searches, at least one must be valid
        """
        if self.searches:
            for search in self.searches:
                if search.is_valid():
                    return True
            return False
"""
See the BuildSA section of this webpage for more information: https://omics.pnl.gov/software/ms-gf

Unlike tide, we specify the enzyme when doing the MSGF+ search, not when building the protein database.
"""
class MSGFPlusIndex(IndexBase):
    __tablename__ = 'MSGFPlusIndex'
    idIndex = Column(Integer, ForeignKey('IndexBase.idIndex'), primary_key=True)
    tda = Column('tda', Integer)
    MSGFPlusIndexName = Column(String, nullable=False, unique=True)
    #MSGFPlusIndexPath is the path to the FASTA, which is in the same place as the files generated by MSGFPlus Index
    MSGFPlusIndexPath = Column(String, nullable=False)
    filteredNetMHCs = relationship('FilteredNetMHC', secondary = msgfplus_index_filteredNetMHC, back_populates = 'msgfplusindices')
    peptidelists = relationship('PeptideList', secondary= msgfplus_index_peptidelists, back_populates = 'msgfplusindices')
    targetsets = relationship('TargetSet', secondary=msgfplus_index_targetset, back_populates='msgfplusindices')
    fasta = relationship('FASTA', secondary=msgfplus_index_fasta, back_populates='msgfplusindices')
    searches = relationship('MSGFPlusSearch', back_populates='index', cascade='all,delete')
    __mapper_args__ = {
        'polymorphic_identity': 'msgfplusindex',
    }
    def is_valid(self):
        if self.searches:
            for search in self.searches:
                if search.is_valid():
                    return True
            return False
    def remove_files(self, project_root):
        delete_objects(project_root, [], [os.path.dirname(self.MSGFPlusIndexPath)])
    def identifier(self):
        return self.MSGFPlusIndexName
class SearchBase(BaseTable):
    __tablename__ = 'SearchBase'
    idSearch = Column('idSearch', Integer, primary_key=True)
    searchType = Column(String(50))
    QValueBases = relationship('QValueBase', back_populates='searchbase', cascade='all,delete')
    SearchName = Column('SearchName', String, unique=True)
    partOfIterativeSearch = Column('partOfIterativeSearch', Boolean, default=False)
    __mapper_args__ = {
        'polymorphic_identity': 'searchbase',
        'polymorphic_on': searchType
    }
    def get_contaminant_sets(self):
        return []
    def identifier(self):
        return self.SearchName
    def __prepare_deletion__(self, project_root):
        if len(self.QValueBases):
            for x in list(self.QValueBases):

                x.__prepare_deletion__(project_root)
        self.remove_files(project_root)

        



class MaxQuantSearch(SearchBase, AbstractPeptideCollection):
    __tablename__ = 'MaxQuantSearch'
    idSearch = Column(Integer, ForeignKey('SearchBase.idSearch'), primary_key=True)
    idRAW = Column('idRAW', Integer, ForeignKey('RAWfile.idRAWfile'))
    idParameterFile = Column('idParameterFile', Integer, ForeignKey('MaxQuantParameterFile.idMaxQuantParameterFile'), nullable=True)
    parameterFile = relationship('MaxQuantParameterFile')
    Path = Column('Path', String, nullable=False)
    raw = relationship('RAWfile')
    fdr = Column('fdr', String, nullable=False)
    filteredNetMHCs = relationship('FilteredNetMHC', secondary = maxquant_search_filteredNetMHC, back_populates = 'maxquantsearches')
    peptidelists = relationship('PeptideList', secondary= maxquant_search_peptidelists, back_populates = 'maxquantsearches')
    targetsets = relationship('TargetSet', secondary=maxquant_search_targetset, back_populates='maxquantsearches')
    contaminants = relationship('ContaminantSet', secondary = maxquantsearch_contaminantSet, back_populates='maxquantsearches')


    def remove_files(self, project_root):
        delete_objects(project_root, [], [self.Path])
    def get_peptides(self, project_path):
        peptides_location = os.path.join(project_path, self.Path, 'combined', 'txt', 'peptides.txt')
        parser_object = MaxQuantPeptidesParser(peptides_location)
        return parser_object.get_peptides()
    __mapper_args__ = {
        'polymorphic_identity': 'maxquantsearch',
    }


    
class TideSearch(SearchBase):
    __tablename__ = 'TideSearch'
    idSearch = Column(Integer, ForeignKey('SearchBase.idSearch'), primary_key=True)
    idTideIndex = Column('idTideIndex', Integer, ForeignKey('TideIndex.idIndex'))
    idParameterFile = Column('idParameterFile', Integer, ForeignKey('TideSearchParameterFile.idTideSearchParameterFile'))
    parameterFile = relationship('TideSearchParameterFile')
    #TideSearchName = Column('TideSearchName', String, unique=True)
    idMGF = Column('idMGF', Integer, ForeignKey('MGFfile.idMGFfile'))
    targetPath = Column('targetPath', String)
    decoyPath = Column('decoyPath', String)
    concat = Column('concat', Boolean, default=False)
    paramsPath = Column('paramsPath', String)
    logPath = Column('logPath', String)
    tideindex = relationship('TideIndex')
    mgf = relationship('MGFfile')
    __mapper_args__ = {
        'polymorphic_identity': 'tidesearch',
    }

    def get_contaminant_sets(self):
        return self.tideindex.contaminants
    def remove_files(self, project_root):
        delete_objects(project_root, [], [os.path.dirname(self.targetPath)])
    def is_valid(self):
        """
        A Tide search is valid if the tide index exists, the parameter file exists, the MGF exists. Additionally, if it was part of an iterative search (that is, partOfIterativeSearch is true), it must be linked to at least one iterative search
        """
        if self.tideindex and  self.parameterFile and self.mgf:
            if self.partOfIterativeSearch:
                session = object_session(self)
                rows = session.query(IterativeRunSearchAssociation).filter_by(search_id = self.idSearch).all()
                if rows:
                    return True
            else:
                return True
        return False

    
class MSGFPlusModificationFile(BaseTable):
    __tablename__ = 'MSGFPlusModificationFile'
    idMSGFPlusModificationFile = Column('idMSGFPlusModificationFile', Integer, primary_key=True)
    MSGFPlusModificationFileName = Column('MSGFPlusModificationFileName', String, unique=True)
    MSGFPlusModificationFilePath = Column('MSGFPlusModificationFilePath', String, unique=True)
    def identifier(self):
        return self.MSGFPlusModificationFileName

    def remove_files(self, project_root):
        delete_objects(project_root, [self.MSGFPlusModificationFilePath])
"""
See "MSGF+ Parameters" section of this: https://omics.pnl.gov/software/ms-gf. 

Note that the tda and ShowQValue options are missing from this table. I did this, because I want these options to always be on.
"""
class MSGFPlusSearch(SearchBase):
    __tablename__ = 'MSGFPlusSearch'
    idSearch = Column(Integer, ForeignKey('SearchBase.idSearch'), primary_key=True)
    idMSGFPlusIndex = Column('idMSGFPlusIndex', Integer, ForeignKey('MSGFPlusIndex.idIndex'))
    idMGF = Column('idMGF', Integer, ForeignKey('MGFfile.idMGFfile'))
    #Output in mzIdentML format
    resultFilePath = Column('resultFilePath', String)
    ParentMassTolerance = Column('ParentMassTolerance', String)
    IsotopeErrorRange = Column('IsotopeErrorRange', String)
    #If NumOfThreads is null, then used default value (which is the number of logical cores on the machine)
    NumOfThreads = Column('NumOfThreads', Integer)
    FragmentationMethodID = Column('FragmentationMethodID', Integer)
    InstrumentID = Column('InstrumentID', Integer)
    EnzymeID = Column('EnzymeID', Integer)
    ProtocolID = Column('ProtocolID', Integer)
    ccm = Column('ccm', String)
    idMSGFPlusModificationFile = Column('idMSGFPlusModificationFile', Integer, ForeignKey('MSGFPlusModificationFile.idMSGFPlusModificationFile'))
    modificationFile = relationship('MSGFPlusModificationFile')
    minPepLength = Column('minPepLength', Integer)
    maxPepLength = Column('maxPepLength', Integer)
    minPrecursorCharge = Column('minPrecursorCharge', Integer)
    maxPrecursorCharge = Column('maxPrecursorCharge', Integer)
    addFeatures = Column('addFeatures', Integer)
    index = relationship('MSGFPlusIndex', back_populates='searches')
    mgf = relationship('MGFfile')
    __mapper_args__ = {
        'polymorphic_identity': 'msgfplussearch',
    }
    def get_contaminant_sets(self):
        return self.index.contaminants
    def remove_files(self, project_root):
        delete_objects(project_root, [], [os.path.dirname(self.resultFilePath)])
    def is_valid(self):
        """
        An MSGF+ search is valid if the MSGF+ index exists, and the MGF exists. Additionally, if it was part of an iterative search (that is, partOfIterativeSearch is true), it must be linked to at least one iterative search
        """
        if self.index and self.mgf:
            print('index and mgf are set')
            if self.partOfIterativeSearch:
                session = object_session(self)
                rows = session.query(IterativeRunSearchAssociation).filter_by(search_id = self.idSearch).all()
                print('rows: ')
                print(rows)
                if rows:
                    return True
            else:
                return True
        return False


class QValueBase(BaseTable):
    __tablename__ = 'QValueBase'
    idQValue = Column('idQValue', Integer, primary_key=True)
    QValueType = Column(String(50))
    filteredSearchResults = relationship('FilteredSearchResult', back_populates='QValue', cascade='all,delete')
    idSearchBase = Column(Integer, ForeignKey('SearchBase.idSearch'))
    searchbase = relationship('SearchBase', back_populates='QValueBases')
    partOfIterativeSearch = Column('partOfIterativeSearch', Boolean, default=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'qvaluebase',
        'polymorphic_on': QValueType
    }
    """
    QValueBase -> SearchBase -> IndexBase -> contaminants

    This returns a list of rows from the  ContaminantSet table
    """
    def get_contaminant_sets(self):
        return self.searchbase.get_contaminant_sets()
    def remove_files(self, project_root):
        pass
    def __prepare_deletion__(self, project_root):
        if self.filteredSearchResults:
            for x in self.filteredSearchResults:
                x.__prepare_deletion__(project_root)

        self.remove_files(project_root)

    def is_valid(self):
        if self.searchbase and self.searchbase.is_valid():
            return True
        else:
            return False


class MSGFPlusQValue(QValueBase):
    __tablename__ = 'MSGFPlusQValue'
    idQValue = Column(Integer, ForeignKey('QValueBase.idQValue'), primary_key=True)
    #the name is the name of the search
    __mapper_args__ = {
        'polymorphic_identity': 'msgfplus',
    }
    
class AssignConfidence(QValueBase):
    __tablename__ = 'AssignConfidence'
    idQValue = Column(Integer, ForeignKey('QValueBase.idQValue'), primary_key=True)
    AssignConfidenceOutputPath = Column('AssignConfidenceOutputPath', String)
    AssignConfidenceName = Column('AssignConfidenceName', String, unique=True)
    idParameterFile = Column('idParameterFile', Integer, ForeignKey('AssignConfidenceParameterFile.idAssignConfidenceParameterFile'))
    parameterFile = relationship('AssignConfidenceParameterFile')
    idSearch = Column('idSearch', Integer, ForeignKey('SearchBase.idSearch'))
    estimation_method = Column(String)
    score = Column(String)
    sidak = Column(String)
    top_match_in = Column(Integer)
    combine_charge_states = Column(String)
    combined_modified_peptides = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'assignconfidence',
    }
    def identifier(self):
        return self.AssignConfidenceName
    def remove_files(self, project_root):
        delete_objects(project_root, [], [self.AssignConfidenceOutputPath])


        
class Percolator(QValueBase):
    __tablename__ = 'Percolator'
    idQValue = Column(Integer, ForeignKey('QValueBase.idQValue'), primary_key=True)
    idSearch = Column('idSearch', Integer, ForeignKey('SearchBase.idSearch'))
    PercolatorName = Column('PercolatorName', String, unique=True)
    PercolatorOutputPath = Column('PercolatorOutputPath', String, unique=True)
    inputParamFilePath = Column('inputParamFilePath', String)
    idParameterFile = Column('idParameterFile', Integer, ForeignKey('PercolatorParameterFile.idPercolatorParameterFile'))
    parameterFile = relationship('PercolatorParameterFile')

    __mapper_args__ = {
        'polymorphic_identity': 'percolator',
    }
    def identifier(self):
        return self.PercolatorName
    def remove_files(self, project_root):
        delete_objects(project_root, [], [self.PercolatorOutputPath])
    

class FilteredSearchResult(BaseTable, AbstractPeptideCollection):
    __tablename__ = 'FilteredSearchResult'
    idFilteredSearchResult = Column('idFilteredSearchResult', Integer, primary_key=True)
    filteredSearchResultName = Column('filteredSearchResultName', String, unique=True)
    filteredSearchResultPath = Column('filteredSearchResultPath', String)
    q_value_threshold = Column('q_value_threshold', Float)
    idQValueBase = Column(Integer, ForeignKey('QValueBase.idQValue'))
    QValue = relationship('QValueBase', back_populates='filteredSearchResults')
    partOfIterativeSearch = Column('partOfIterativeSearch', Boolean, default=False)

    def get_contaminant_sets(self):
        return self.QValue.get_contaminant_sets()

    def is_valid(self):
        if self.QValue and self.QValue.is_valid():
            return True
        else:
            return False
    def __prepare_deletion__(self, project_root):
        self.remove_files(project_root)
    def remove_files(self, project_root):
        delete_objects(project_root, [self.filteredSearchResultPath])
    def identifier(self):
        return self.filteredSearchResultName
    
    def get_peptides(self, project_path):
        peptides = set()
        with open(os.path.join(project_path, self.filteredSearchResultPath), 'r') as f:
            for line in f:
                stripped_line = line.strip()
                if len(stripped_line) >= 1:
                    peptides.add(stripped_line)
        return peptides
    
class Command(BaseTable):
    __tablename__ = 'Command'
    idCommand = Column('idCommand', Integer, primary_key=True)
    executionDateTime = Column('executionDateTime', DateTime, default=datetime.datetime.utcnow)
    commandString = Column('commandString', String)
    executionSuccess = Column('executionSuccess', Integer, default=0)
    def __repr__(self):
        return str(self.idCommand) + ' | ' + self.executionDateTime.strftime('%A %d, %B %Y') + ' | ' + self.commandString + ' | ' + str(self.executionSuccess)
def init_session(db_path):
    engine = create_engine('sqlite:///' + db_path)
    BaseTable.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

#session = init_session('new_test/database.db')
#a = session.query(FilteredNetMHC, NetMHC, HLA).join(NetMHC).join(HLA).filter(HLA.HLAName=='HLA-A0101').all()



#session.commit()
#engine = create_engine('sqlite:///database.db', echo=True)
#BaseTable.metadata.create_all(engine)
#Session = sessionmaker(bind=engine)
