from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, create_engine, Float, BLOB, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
Base = declarative_base()



tideindex_filteredNetMHC = Table('tideindex_filteredNetMHC', Base.metadata, Column('tideindex_id', ForeignKey('TideIndex.idTideIndex'), primary_key=True), Column('filteredNetMHC_id', ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))

tideindex_peptidelists = Table('tideindex_peptidelists', Base.metadata, Column('tideindex_id', ForeignKey('TideIndex.idTideIndex'), primary_key=True), Column('peptidelist_id', ForeignKey('PeptideList.idPeptideList'), primary_key=True))


"""
Need to add the following 3 tables in database revision 8d70dec8ab88
"""
tideindex_targetset = Table('tideindex_targetset', Base.metadata, Column('tideindex_id', ForeignKey('TideIndex.idTideIndex'), primary_key = True), Column('targetset_id', ForeignKey('TargetSet.idTargetSet'), primary_key=True))

targetset_filteredNetMHC = Table('targetset_filteredNetMHC', Base.metadata, Column('targetset_id', ForeignKey('TargetSet.idTargetSet'), primary_key = True), Column('filteredNetMHC_id', ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))

targetset_peptidelists = Table('targetset_peptidelists', Base.metadata, Column('targetset_id', ForeignKey('TargetSet.idTargetSet'), primary_key = True), Column('peptideList_id', ForeignKey('PeptideList.idPeptideList'), primary_key=True))


class TargetSet(Base):
    __tablename__ = 'TargetSet'
    idTargetSet = Column('idTargetSet', Integer, primary_key = True)
    TargetSetFASTAPath = Column('TargetSetFASTAPath', String, unique=True)
    """
    Each source will be represented by an ASCII character. the SourceSymbolMap row will contain JSON that maps each character to a tuple of the form: ('FilteredNetMHC', 'FilteredNetMHCName') or ('PeptideList', 'PeptideListName'). PeptideSourceMapPath will contain the path to a JSON file that maps each peptide to a string of sources. 

    I realize that this probably isn't the most efficient way of doing this, but it should work for now.
    """
    PeptideSourceMapPath = Column('PeptideSourceMapPath', String)
    SourceSymbolMap = Column('SourceSymbolMap', String)
    filteredNetMHCs = relationship('FilteredNetMHC', secondary=targetset_filteredNetMHC, back_populates='targetsets')
    peptideLists = relationship('PeptideList', secondary=targetset_peptidelists, back_populates='targetsets')
class HLA(Base):
    __tablename__ = 'HLA'
    idHLA = Column('idHLA', Integer, primary_key = True)
    HLAName = Column('HLAName', String, unique=True)

    def __repr__(self):
        return 'MHC ' + self.HLAName


class MGFfile(Base):
    __tablename__ = 'MGFfile'
    idMGFfile = Column('idMGFfile', Integer, primary_key=True)
    MGFName = Column('MGFName', String, unique=True)
    MGFPath = Column('MGFPath', String)
    def __repr__(self):
        return 'MGF File found at: ' + self.MGFPath

class FASTA(Base):
    __tablename__ = 'FASTA'
    idFASTA = Column('idFASTA', Integer, primary_key=True)
    Name = Column('Name', String, unique=True)
    FASTAPath = Column('FASTAPath',  String, unique=True)
    Comment = Column('Comment', String)
    peptide_lists = relationship('PeptideList', back_populates='fasta')
    def __repr__(self):
        return 'FASTA File found at: ' + self.FASTAPath + ' with comment: ' + self.Comment

class PeptideList(Base):
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
    def __repr__(self):
        return 'Peptide List can be found at: ' + self.PeptideListPath


class NetMHC(Base):
    __tablename__ = 'NetMHC'
    idNetMHC = Column('idNetMHC', Integer, primary_key = True)
    peptidelistID = Column('peptideListID', Integer, ForeignKey('PeptideList.idPeptideList'))
    idHLA = Column('idHLA', Integer, ForeignKey('HLA.idHLA'))
    #Raw output of NetMHC
    NetMHCOutputPath = Column('NetMHCOutputPath', String)
    #a TXT file, each line is a peptide, then a comma, then the rank
    PeptideScorePath = Column('HighScoringPeptidesPath', String)
    
class FilteredNetMHC(Base):
    __tablename__ = 'FilteredNetMHC'
    idFilteredNetMHC = Column('idFilteredNetMHC', Integer, primary_key=True)
    idNetMHC = Column('idNetMHC', Integer, ForeignKey('NetMHC.idNetMHC'))
    filtered_path = Column('filtered_path', String)
    FilteredNetMHCName = Column('FilteredNetMHCName', String)
    RankCutoff = Column('RankCutoff', Float)
    tideindices = relationship('TideIndex', secondary=tideindex_filteredNetMHC, back_populates='filteredNetMHCs')
    targetsets = relationship('TargetSet', secondary=targetset_filteredNetMHC, back_populates='filteredNetMHCs')
class TideIndex(Base):
    __tablename__ = 'TideIndex'
    idTideIndex = Column('idTideIndex', Integer, primary_key=True)
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
    
class TideSearch(Base):
    __tablename__ = 'TideSearch'
    idTideSearch = Column('idTideSearch', Integer, primary_key=True)
    idTideIndex = Column('idTideIndex', Integer, ForeignKey('TideIndex.idTideIndex'))
    TideSearchName = Column('TideSearchName', String, unique=True)
    idMGF = Column('idMGF', Integer, ForeignKey('MGFfile.idMGFfile'))
    targetPath = Column('targetPath', String)
    decoyPath = Column('decoyPath', String)
    paramsPath = Column('paramsPath', String)
    logPath = Column('logPath', String)
    tideIndex = relationship('TideIndex')
    mgf = relationship('MGFfile')
class AssignConfidence(Base):
    __tablename__ = 'AssignConfidence'
    idAssignConfidence = Column('idAssignConfidence', Integer, primary_key=True)
    AssignConfidenceOutputPath = Column('AssignConfidenceOutputPath', String)
    AssignConfidenceName = Column('AssignConfidenceName', String, unique=True)
    idTideSearch = Column('idTideSearch', Integer, ForeignKey('TideSearch.idTideSearch'))
    estimation_method = Column(String)
    score = Column(String)
    sidak = Column(String)
    top_match_in = Column(Integer)
    combine_charge_states = Column(String)
    combined_modified_peptides = Column(String)
    tideSearch = relationship('TideSearch')
    
class Percolator(Base):
    __tablename__ = 'Percolator'
    idPercolator = Column('idPercolator', Integer, primary_key=True)
    idTideSearch = Column('idTideSearch', Integer, ForeignKey('TideSearch.idTideSearch'))
    targetPeptidesPath = Column('targetPeptidesPath', String)
    decoyPeptidesPath = Column('decoyPeptidesPath', String)
    targetPSMSPath = Column('targetPSMSPath', String)
    decoyPSMSPath = Column('decoyPSMSPath', String)
    paramsPath = Column('paramsPath', String)
    pepXMLPath = Column('pepXMLPath', String)
    logPath = Column('logPath', String)


class Command(Base):
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

session = Session()
 human = Species(SpeciesName = 'human')
common_hla = HLA(HLAName = 'HLA A*0101', species=[human])
abc_hypersens = HLA(HLAName = 'HLA B*5701', species=[human])
session.add(human)
session.add(common_hla)
session.add(abc_hypersens)
session.commit()
print(common_hla)
"""
