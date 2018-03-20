from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, create_engine, Float, BLOB, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
Base = declarative_base()


species_hla = Table('species_hla', Base.metadata,
     Column('species_id', ForeignKey('Species.idSpecies'), primary_key=True),
     Column('HLA_id', ForeignKey('HLA.idHLA'), primary_key=True)
)

peptidelist_netmhc = Table('peptidelist_netmhc', Base.metadata,
                           Column('peptidelist_id', ForeignKey('PeptideList.idPeptideList'), primary_key=True),
                           Column('netmhc_id', ForeignKey('NetMHC.idNetMHC'), primary_key=True)                    
)

tideindex_filteredNetMHC = Table('tideindex_filteredNetMHC', Base.metadata, Column('tideindex_id', ForeignKey('TideIndex.idTideIndex'), primary_key=True), Column('filteredNetMHC_id', ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))

tideindex_peptidelists = Table('tideindex_peptidelists', Base.metadata, Column('tideindex_id', ForeignKey('TideIndex.idTideIndex'), primary_key=True), Column('peptidelist_id', ForeignKey('PeptideList.idPeptideList'), primary_key=True))
class Species(Base):
    __tablename__ = 'Species'
    idSpecies = Column('idSpecies', Integer, primary_key=True)
    SpeciesName = Column('SpeciesName', String, unique=True)

    hlas = relationship('HLA',
                       secondary=species_hla,
                       back_populates='species')
    def __repr__(self):
        return 'Species: ' + self.SpeciesName



class HLA(Base):
    __tablename__ = 'HLA'
    idHLA = Column('idHLA', Integer, primary_key = True)
    HLAName = Column('HLAName', String, unique=True)
    species = relationship('Species',
                       secondary=species_hla,
                       back_populates='hlas')
    def __repr__(self):
        return 'MHC ' + self.HLAName + ' from species: ' + self.species[0].SpeciesName


class MGFfile(Base):
    __tablename__ = 'MGFfile'
    idMGFfile = Column('idMGFfile', Integer, primary_key=True)
    MGFName = Column('MGFName', String, unique=True)
    MGFPath = Column('MGFPath', String, unique=True)
    def __repr__(self):
        return 'MGF File found at: ' + self.MGFPath

class FASTA(Base):
    __tablename__ = 'FASTA'
    idFASTA = Column('idFASTA', Integer, primary_key=True)
    Name = Column('Name', String, unique=True)
    FASTAPath = Column('FASTAPath',  String, unique=True)
    Comment = Column('Comment', String)

    def __repr__(self):
        return 'FASTA File found at: ' + self.FASTAPath + ' with comment: ' + self.Comment

class PeptideList(Base):
    __tablename__ = 'PeptideList'
    idPeptideList = Column('idPeptideList', Integer, primary_key=True)
    userPeptideListID = Column('userPeptideListID', Integer, unique=True)
    idFASTA = Column('idFASTA', Integer, ForeignKey('FASTA.idFASTA'))
    PeptideListPath = Column('PeptideListPath', String)
    #Just a string of integers seperated by spaces. 
    lengths = Column('lengths', String)
    netmhcs = relationship('NetMHC', secondary=peptidelist_netmhc, back_populates='peptidelists')

    tideindices = relationship('TideIndex', secondary=tideindex_peptidelists, back_populates='peptidelists')
    def __repr__(self):
        return 'Peptide List can be found at: ' + self.PeptideListPath


class NetMHC(Base):
    __tablename__ = 'NetMHC'
    idNetMHC = Column('idNetMHC', Integer, primary_key = True)
    peptidelists = relationship('PeptideList',
                        secondary=peptidelist_netmhc,
                        back_populates='netmhcs')
    idHLA = Column('idHLA', Integer, ForeignKey('HLA.idHLA'))
    #Raw output of NetMHC
    NetMHCOutputPath = Column('NetMHCOutputPath', String)
    #a TXT file, each line is a peptide, then a comma, then the rank
    PeptideScorePath = Column('HighScoringPeptidesPath', String)
    
class FilteredNetMHC(Base):
    #this is a rather abstract thing -- we don't actually store the filtered values peptides, since filtering them by their rank is a quick task once we already know their ranks
    __tablename__ = 'FilteredNetMHC'
    idFilteredNetMHC = Column('idFilteredNetMHC', Integer, primary_key=True)
    idNetMHC = Column('idNetMHC', Integer, ForeignKey('NetMHC.idNetMHC'))
    RankCutoff = Column('RankCutoff', Float)
    tideindices = relationship('TideIndex', secondary=tideindex_filteredNetMHC, back_populates='filteredNetMHCs')
class TideIndex(Base):
    __tablename__ = 'TideIndex'
    idTideIndex = Column('idTideIndex', Integer, primary_key=True)
    TideIndexPath = Column('TideIndexPath', String)
    TideIndexOptions = Column('TideIndexOptions', BLOB)
    
    filteredNetMHCs = relationship('FilteredNetMHC', secondary = tideindex_filteredNetMHC, back_populates = 'tideindices')
    peptidelists = relationship('PeptideList', secondary= tideindex_peptidelists, back_populates = 'tideindices')

    
class TideSearch(Base):
    __tablename__ = 'TideSearch'
    idTideSearch = Column('idTideSearch', Integer, primary_key=True)
    idTideIndex = Column('idTideIndex', Integer, ForeignKey('TideIndex.idTideIndex'))
    idMGF = Column('idMGF', Integer, ForeignKey('MGFfile.idMGFfile'))
    numMatches = Column('numMatches', Integer)
    targetPath = Column('targetPath', String)
    decoyPath = Column('decoyPath', String)
    paramsPath = Column('paramsPath', String)
    logPath = Column('logPath', String)

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
