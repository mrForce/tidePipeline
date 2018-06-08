from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, create_engine, Float, BLOB, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
from abc import ABCMeta, abstractmethod
import os
BaseTable = declarative_base(metaclass=ABCMeta)


class AbstractPeptideCollection(BaseTable):
    __abstract__ = True
    #get_peptides should return a set of peptides. Each peptide is a string.
    @abstractmethod
    def get_peptides(self, project_path):
        pass


    


tideindex_filteredNetMHC = Table('tideindex_filteredNetMHC', BaseTable.metadata, Column('tideindex_id', ForeignKey('TideIndex.idIndex'), primary_key=True), Column('filteredNetMHC_id', ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))

msgfplus_index_filteredNetMHC = Table('msgfplus_index_filteredNetMHC', BaseTable.metadata, Column('msgfplus_index_id', ForeignKey('MSGFPlusIndex.idIndex'), primary_key=True), Column('filteredNetMHC_id', ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))

tideindex_peptidelists = Table('tideindex_peptidelists', BaseTable.metadata, Column('tideindex_id', ForeignKey('TideIndex.idIndex'), primary_key=True), Column('peptidelist_id', ForeignKey('PeptideList.idPeptideList'), primary_key=True))


msgfplus_index_peptidelists = Table('msgfplus_index_peptidelists', BaseTable.metadata, Column('msgfplus_index_id', ForeignKey('MSGFPlusIndex.idIndex'), primary_key=True), Column('peptidelist_id', ForeignKey('PeptideList.idPeptideList'), primary_key=True))


"""
Need to add the following 3 tables in database revision 8d70dec8ab88
"""
tideindex_targetset = Table('tideindex_targetset', BaseTable.metadata, Column('tideindex_id', ForeignKey('TideIndex.idIndex'), primary_key = True), Column('targetset_id', ForeignKey('TargetSet.idTargetSet'), primary_key=True))

msgfplus_index_targetset = Table('msgfplus_index_targetset', BaseTable.metadata, Column('msgfplus_index_id', ForeignKey('MSGFPlusIndex.idIndex'), primary_key = True), Column('targetset_id', ForeignKey('TargetSet.idTargetSet'), primary_key=True))

targetset_filteredNetMHC = Table('targetset_filteredNetMHC', BaseTable.metadata, Column('targetset_id', ForeignKey('TargetSet.idTargetSet'), primary_key = True), Column('filteredNetMHC_id', ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))

targetset_peptidelists = Table('targetset_peptidelists', BaseTable.metadata, Column('targetset_id', ForeignKey('TargetSet.idTargetSet'), primary_key = True), Column('peptideList_id', ForeignKey('PeptideList.idPeptideList'), primary_key=True))


class TargetSet(AbstractPeptideCollection):
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

    def __repr__(self):
        return 'MHC ' + self.HLAName


class MGFfile(BaseTable):
    __tablename__ = 'MGFfile'
    idMGFfile = Column('idMGFfile', Integer, primary_key=True)
    MGFName = Column('MGFName', String, unique=True)
    MGFPath = Column('MGFPath', String)
    def __repr__(self):
        return 'MGF File found at: ' + self.MGFPath

class FASTA(BaseTable):
    __tablename__ = 'FASTA'
    idFASTA = Column('idFASTA', Integer, primary_key=True)
    Name = Column('Name', String, unique=True)
    FASTAPath = Column('FASTAPath',  String, unique=True)
    Comment = Column('Comment', String)
    peptide_lists = relationship('PeptideList', back_populates='fasta')
    def __repr__(self):
        return 'FASTA File found at: ' + self.FASTAPath + ' with comment: ' + self.Comment

class PeptideList(AbstractPeptideCollection):
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
    def __repr__(self):
        return 'Peptide List can be found at: ' + self.PeptideListPath

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
    idHLA = Column('idHLA', Integer, ForeignKey('HLA.idHLA'))
    hla = relationship('HLA')
    #Raw output of NetMHC
    NetMHCOutputPath = Column('NetMHCOutputPath', String)
    #a TXT file, each line is a peptide, then a comma, then the rank
    PeptideScorePath = Column('PeptideScorePath', String)
    peptidelist = relationship('PeptideList')
class FilteredNetMHC(BaseTable):
    __tablename__ = 'FilteredNetMHC'
    idFilteredNetMHC = Column('idFilteredNetMHC', Integer, primary_key=True)
    idNetMHC = Column(Integer, ForeignKey('NetMHC.idNetMHC'))
    filtered_path = Column('filtered_path', String)
    FilteredNetMHCName = Column('FilteredNetMHCName', String)
    RankCutoff = Column('RankCutoff', Float)
    tideindices = relationship('TideIndex', secondary=tideindex_filteredNetMHC, back_populates='filteredNetMHCs')
    targetsets = relationship('TargetSet', secondary=targetset_filteredNetMHC, back_populates='filteredNetMHCs')
    msgfplusindices = relationship('MSGFPlusIndex', secondary=msgfplus_index_filteredNetMHC, back_populates='filteredNetMHCs')
    netmhc = relationship('NetMHC')
class IndexBase(BaseTable):
    __tablename__ = 'IndexBase'
    idIndex = Column('idIndex', Integer, primary_key=True)
    indexType = Column(String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'indexbase',
        'polymorphic_on': indexType
    }
class TideIndex(IndexBase):
    __tablename__ = 'TideIndex'
    idIndex = Column(Integer, ForeignKey('IndexBase.idIndex'), primary_key=True)
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
    __mapper_args__ = {
        'polymorphic_identity': 'tideindex',
    }
"""
See the BuildSA section of this webpage for more information: https://omics.pnl.gov/software/ms-gf

Unlike tide, we specify the enzyme when doing the MSGF+ search, not when building the protein database.
"""
class MSGFPlusIndex(IndexBase):
    __tablename__ = 'MSGFPlusIndex'
    idIndex = Column(Integer, ForeignKey('IndexBase.idIndex'), primary_key=True)
    tda = Column('tda', Integer)
    filteredNetMHCs = relationship('FilteredNetMHC', secondary = msgfplus_index_filteredNetMHC, back_populates = 'msgfplusindices')
    peptidelists = relationship('PeptideList', secondary= msgfplus_index_peptidelists, back_populates = 'msgfplusindices')
    targetsets = relationship('TargetSet', secondary=msgfplus_index_targetset, back_populates='msgfplusindices')
    __mapper_args__ = {
        'polymorphic_identity': 'msgfplusindex',
    }


class SearchBase(BaseTable):
    __tablename__ = 'SearchBase'
    idSearch = Column('idSearch', Integer, primary_key=True)
    searchType = Column(String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'searchbase',
        'polymorphic_on': searchType
    }

    
class TideSearch(SearchBase):
    __tablename__ = 'TideSearch'
    idSearch = Column(Integer, ForeignKey('SearchBase.idSearch'), primary_key=True)
    idTideIndex = Column('idTideIndex', Integer, ForeignKey('TideIndex.idIndex'))
    TideSearchName = Column('TideSearchName', String, unique=True)
    idMGF = Column('idMGF', Integer, ForeignKey('MGFfile.idMGFfile'))
    targetPath = Column('targetPath', String)
    decoyPath = Column('decoyPath', String)
    paramsPath = Column('paramsPath', String)
    logPath = Column('logPath', String)
    tideIndex = relationship('TideIndex')
    mgf = relationship('MGFfile')
    __mapper_args__ = {
        'polymorphic_identity': 'tidesearch',
    }
class MSGFPlusModificationFile(BaseTable):
    __tablename__ = 'MSGFPlusModificationFile'
    idMSGFPlusModificationFile = Column('idMSGFPlusModificationFile', Integer, primary_key=True)
    MSGFPlusModificationFileName = Column('MSGFPlusModificationFileName', String, unique=True)
    MSGFPlusModificationFilePath = Column('MSGFPlusModificationFilePath', String, unique=True)
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
    ntt = Column('ntt', Integer)
    idMSGFPlusModificationFile = Column('idMSGFPlusModificationFile', Integer, ForeignKey('MSGFPlusModificationFile.idMSGFPlusModificationFile'))
    minPepLength = Column('minPepLength', Integer)
    maxPepLength = Column('maxPepLength', Integer)
    minPrecursorCharge = Column('minPrecursorCharge', Integer)
    maxPrecursorCharge = Column('maxPrecursorCharge', Integer)
    MSGFPlusQValue = relationship('MSGFPlusQValue', uselist=False, back_populates='MSGFPlusSearch')
    __mapper_args__ = {
        'polymorphic_identity': 'msgfplussearch',
    }

class QValueBase(BaseTable):
    __tablename__ = 'QValueBase'
    idQValue = Column('idQValue', Integer, primary_key=True)
    QValueType = Column(String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'qvaluebase',
        'polymorphic_on': QValueType
    }


class MSGFPlusQValue(QValueBase):
    __tablename__ = 'MSGFPlusQValue'
    idQValue = Column(Integer, ForeignKey('QValueBase.idQValue'), primary_key=True)
    MSGFPlusSearch = relationship('MSGFPlusSearch', back_populates='MSGFPlusQValue')
    
class AssignConfidence(QValueBase):
    __tablename__ = 'AssignConfidence'
    idQValue = Column(Integer, ForeignKey('QValueBase.idQValue'), primary_key=True)
    AssignConfidenceOutputPath = Column('AssignConfidenceOutputPath', String)
    AssignConfidenceName = Column('AssignConfidenceName', String, unique=True)
    idTideSearch = Column('idTideSearch', Integer, ForeignKey('TideSearch.idSearch'))
    estimation_method = Column(String)
    score = Column(String)
    sidak = Column(String)
    top_match_in = Column(Integer)
    combine_charge_states = Column(String)
    combined_modified_peptides = Column(String)
    search = relationship('SearchBase')
    __mapper_args__ = {
        'polymorphic_identity': 'assignconfidence',
    }


    
class Percolator(QValueBase):
    __tablename__ = 'Percolator'
    idQValue = Column(Integer, ForeignKey('QValueBase.idQValue'), primary_key=True)
    idSearch = Column('idSearch', Integer, ForeignKey('TideSearch.idSearch'))
    PercolatorName = Column('PercolatorName', String, unique=True)
    PercolatorOutputPath = Column('PercolatorOutputPath', String, unique=True)
    inputParamFilePath = Column('inputParamFilePath', String)
    search = relationship('SearchBase')
    __mapper_args__ = {
        'polymorphic_identity': 'percolator',
    }


class FilteredSearchResult(AbstractPeptideCollection):
    __tablename__ = 'FilteredSearchResult'
    idFilteredSearchResult = Column('idFilteredSearchResult', Integer, primary_key=True)
    filteredSearchResultName = Column('filteredSearchResultName', String, unique=True)
    filteredSearchResultPath = Column('filteredSearchResultPath', String)
    q_value_threshold = Column('q_value_threshold', Float)
    QValue = relationship('QValueBase', uselist=False)
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
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


"""
engine = create_engine('sqlite://', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
"""
