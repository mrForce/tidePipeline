from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, create_engine, Float, BLOB
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


species_hla = Table('species_hla', Base.metadata,
     Column('species_id', ForeignKey('Species.idSpecies'), primary_key=True),
     Column('HLA_id', ForeignKey('HLA.idHLA'), primary_key=True)
)

peptidelist_netmhc = Table('peptidelist_netmhc', Base.metadata,
                           Column('peptidelist_id', ForeignKey('PeptideList.idPeptideList'), primary_key=True),
                           Column('netmhc_id', ForeignKey('NetMHC.idNetMHC'), primary_key=True)                    
)
class Species(Base):
    __tablename__ = 'Species'
    idSpecies = Column('idSpecies', Integer, primary_key=True)
    SpeciesName = Column('SpeciesName', String)

    hlas = relationship('HLA',
                       secondary=species_hla,
                       back_populates='species')
    def __repr__(self):
        return 'Species: ' + self.SpeciesName



class HLA(Base):
    __tablename__ = 'HLA'
    idHLA = Column('idHLA', Integer, primary_key = True)
    HLAName = Column('HLAName', String)
    species = relationship('Species',
                       secondary=species_hla,
                       back_populates='hlas')
    def __repr__(self):
        return 'MHC ' + self.HLAName + ' from species: ' + self.species[0].SpeciesName


class MGFfile(Base):
    __tablename__ = 'MGFfile'
    idMGFfile = Column('idMGFfile', Integer, primary_key=True)
    MGFPath = Column('MGFPath', String)

    def __repr__(self):
        return 'MGF File found at: ' + self.MGFPath

class FASTA(Base):
    __tablename__ = 'FASTA'
    idFASTA = Column('idFASTA', Integer, primary_key=True)
    Name = Column('Name', String)
    FASTAPath = Column('FASTAPath',  String)
    Comment = Column('Comment', String)

    def __repr__(self):
        return 'FASTA File found at: ' + self.FASTAPath + ' with comment: ' + self.Comment

class PeptideList(Base):
    __tablename__ = 'PeptideList'
    idPeptideList = Column('idPeptideList', Integer, primary_key=True)
    idFASTA = Column('idFASTA', Integer, ForeignKey('FASTA.idFASTA'))
    PeptideListPath = Column('PeptideListPath', String)
    netmhcs = relationship('NetMHC', secondary=peptidelist_netmhc, back_populates='peptidelists')
    def __repr__(self):
        return 'Peptide List can be found at: ' + self.PeptideListPath


class NetMHC(Base):
    __tablename__ = 'NetMHC'
    idNetMHC = Column('idNetMHC', Integer, primary_key = True)
    peptidelists = relationship('HLA',
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

class TideIndex(Base):
    __tablename__ = 'TideIndex'
    idTideIndex = Column('idTideIndex', Integer, primary_key=True)
    TideIndexPath = Column('TideIndexPath', String)
    TideIndexOptions = Column('TideIndexOptions', BLOB)

    filteredNetMHCs = relationship('FilteredNetMHC')
    peptidelists = relationship('PeptideList')
    




engine = create_engine('sqlite://', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
"""
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
