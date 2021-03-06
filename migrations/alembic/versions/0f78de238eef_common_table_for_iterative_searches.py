"""Common table for iterative searches

Revision ID: 0f78de238eef
Revises: e3c40c09577d
Create Date: 2018-08-17 14:45:12.540349

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, create_engine, Float, BLOB, DateTime, Boolean

# revision identifiers, used by Alembic.
revision = '0f78de238eef'
down_revision = 'e3c40c09577d'
branch_labels = None
depends_on = None



BaseTable = declarative_base()

class SearchBase(BaseTable):
    __tablename__ = 'SearchBase'
    idSearch = Column('idSearch', Integer, primary_key=True)
    searchType = Column(String(50))
    QValueBases = relationship('QValueBase', back_populates='searchbase', cascade='all,delete')
    SearchName = Column('SearchName', String, unique=True)

class QValueBase(BaseTable):
    __tablename__ = 'QValueBase'
    idQValue = Column('idQValue', Integer, primary_key=True)
    idSearchBase = Column(Integer, ForeignKey('SearchBase.idSearch'))
    searchbase = relationship('SearchBase', back_populates='QValueBases')
    filteredSearchResults = relationship('FilteredSearchResult', back_populates='QValue', cascade='all,delete')

class FilteredSearchResult(BaseTable):
    __tablename__ = 'FilteredSearchResult'
    idFilteredSearchResult = Column('idFilteredSearchResult', Integer, primary_key=True)
    idQValueBase = Column(Integer, ForeignKey('QValueBase.idQValue'))
    QValue = relationship('QValueBase', back_populates='filteredSearchResults')
"""
class IterativeSearchRun_(BaseTable):
    __tablename__ = 'IterativeSearchRun'
    idIterativeSearchRun = Column('idIterativeSearchRun', Integer, primary_key=True)
    IterativeSearchRunName = Column('IterativeSearchRunName', String, unique=True)
    searchType = Column(String(50))
    IterativeFilteredSearchAssociations = relationship('IterativeFilteredSearchAssociation', cascade='all,delete')
    IterativeRunMGFAssociations = relationship('IterativeRunMGFAssociations', cascade='all,delete')
"""

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('IterativeSearchRun',
    sa.Column('idIterativeSearchRun', sa.Integer(), nullable=False),
    sa.Column('IterativeSearchRunName', sa.String(), nullable=True),
    sa.Column('searchType', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('idIterativeSearchRun'),
    sa.UniqueConstraint('IterativeSearchRunName')
    )
    op.create_table('IterativeRunMGFAssociation',
    sa.Column('iterativerun_id', sa.Integer(), nullable=False),
    sa.Column('mgf_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['iterativerun_id'], ['IterativeSearchRun.idIterativeSearchRun'], ),
    sa.ForeignKeyConstraint(['mgf_id'], ['MGFfile.idMGFfile'], ),
    sa.PrimaryKeyConstraint('iterativerun_id', 'mgf_id')
    )
    op.create_table('IterativeRunSearchAssociation',
    sa.Column('iterativerun_id', sa.Integer(), nullable=False),
    sa.Column('search_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['iterativerun_id'], ['IterativeSearchRun.idIterativeSearchRun'], ),
    sa.ForeignKeyConstraint(['search_id'], ['SearchBase.idSearch'], ),
    sa.PrimaryKeyConstraint('iterativerun_id', 'search_id')
    )
    op.create_table('IterativeFilteredSearchAssociation',
    sa.Column('iterative_id', sa.Integer(), nullable=False),
    sa.Column('filteredsearch_id', sa.Integer(), nullable=False),
    sa.Column('step', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['filteredsearch_id'], ['FilteredSearchResult.idFilteredSearchResult'], ),
    sa.ForeignKeyConstraint(['iterative_id'], ['IterativeSearchRun.idIterativeSearchRun'], ),
    sa.PrimaryKeyConstraint('iterative_id', 'filteredsearch_id')
    )
    print('created tables')
    connection = op.get_bind()
    Session = sessionmaker(bind=connection) 
    session = Session()
    metadata = sa.MetaData()
    with op.batch_alter_table('MSGFPlusIterativeRun', schema=None) as batch_op:
        batch_op.add_column(sa.Column('idIterativeSearchRun', sa.Integer(), autoincrement=True))
    with op.batch_alter_table('TideIterativeRun', schema=None) as batch_op:
        batch_op.add_column(sa.Column('idIterativeSearchRun', sa.Integer(), autoincrement=True))

    iterative_run_mgf_association_inserts = []
    iterative_run_search_association_inserts = []
    iterative_filtered_search_association_inserts = []
    iterative_search_run_inserts = []

    iterative_search_run = sa.Table('IterativeSearchRun', metadata, sa.Column('idIterativeSearchRun', sa.Integer, primary_key=True), sa.Column('IterativeSearchRunName', sa.String), sa.Column('searchType', sa.String(50)))
    tide_iterative_run = sa.Table('TideIterativeRun', metadata, sa.Column('idTideIterativeRun', sa.Integer, primary_key=True), sa.Column('idIterativeSearchRun', sa.Integer), sa.Column('TideRunName', sa.String), sa.Column('idMGF', sa.Integer, sa.ForeignKey('MGFfile.idMGFfile')))
    msgf_iterative_run = sa.Table('MSGFPlusIterativeRun', metadata, sa.Column('idMSGFPlusIterativeRun', sa.Integer, primary_key=True), sa.Column('idIterativeSearchRun', sa.Integer), sa.Column('MSGFPlusIterativeRunName', sa.String), sa.Column('idMGF', sa.Integer, sa.ForeignKey('MGFfile.idMGFfile')))
    msgf_iterative_run_mgf_association = sa.Table('MSGFPlusIterativeRunMGFAssociation', metadata, sa.Column('msgfiterativerun_id', sa.Integer, sa.ForeignKey('MSGFPlusIterativeRun.idMSGFPlusIterativeRun'), primary_key=True), sa.Column('mgf_id', sa.Integer, sa.ForeignKey('MGFfile.idMGFfile'), primary_key=True))
    tide_iterative_run_mgf_association = sa.Table('TideIterativeRunMGFAssociation', metadata, sa.Column('tideiterativerun_id', sa.Integer, sa.ForeignKey('TideIterativeRun.idTideIterativeRun'), primary_key=True), sa.Column('mgf_id', sa.Integer, sa.ForeignKey('MGFfile.idMGFfile'), primary_key=True))
    msgf_iterative_run_filteredsearch_association = sa.Table('MSGFPlusIterativeFilteredSearchAssociation', metadata, sa.Column('msgfplusiterative_id', sa.Integer, sa.ForeignKey('MSGFPlusIterativeRun.idMSGFPlusIterativeRun'), primary_key=True), sa.Column('filteredsearch_id', sa.Integer, sa.ForeignKey('FilteredSearchResult.idFilteredSearchResult'), primary_key=True), sa.Column('step', sa.Integer))

    tide_iterative_filteredsearch_association = sa.Table('TideIterativeFilteredSearchAssociation', metadata, sa.Column('tideiterative_id', sa.Integer, sa.ForeignKey('TideIterativeRun.idTideIterativeRun'), primary_key=True), sa.Column('filteredsearch_id', sa.Integer, sa.ForeignKey('FilteredSearchResult.idFilteredSearchResult'), primary_key=True), sa.Column('step', sa.Integer))
    print('going to find max ID')
    max_id = 0
    for row in connection.execute(sa.select([tide_iterative_run])):
        op.execute(tide_iterative_run.update().where(tide_iterative_run.c.idTideIterativeRun == row.idTideIterativeRun).values({'idIterativeSearchRun': row.idTideIterativeRun}))
        if row.idTideIterativeRun > max_id:
            max_id = row.idTideIterativeRun
    for row in connection.execute(sa.select([msgf_iterative_run])):
        if row.idMSGFPlusIterativeRun > max_id:
            max_id = row.idMSGFPlusIterativeRun
    print('got max id')
    """
    Assign new IDs to the rows in MSGFPlusIterativeRun. Change the IDs in MSGFPlusIterativeRunMGFAssociation and MSGFPlusIterativeFilteredSearchAssociation
    """
    new_id = max_id + 1
    for row in list(connection.execute(sa.select([msgf_iterative_run]))):
        print(row)
        old_id = row.idMSGFPlusIterativeRun
        op.execute(msgf_iterative_run.update().where(msgf_iterative_run.c.idMSGFPlusIterativeRun == old_id).values({'idMSGFPlusIterativeRun': new_id, 'idIterativeSearchRun': new_id}))
        op.execute(msgf_iterative_run_mgf_association.update().where(msgf_iterative_run_mgf_association.c.msgfiterativerun_id == old_id).values({'msgfiterativerun_id': new_id}))
        op.execute(msgf_iterative_run_filteredsearch_association.update().where(msgf_iterative_run_filteredsearch_association.c.msgfplusiterative_id == old_id).values({'msgfplusiterative_id': new_id}))
        new_id += 1

    for row in list(connection.execute(sa.select([msgf_iterative_run]))):
        iterative_search_run_inserts.append({'idIterativeSearchRun': row.idMSGFPlusIterativeRun, 'IterativeSearchRunName': row.MSGFPlusIterativeRunName, 'searchType': 'msgf'})
    for row in list(connection.execute(sa.select([tide_iterative_run]))):
        iterative_search_run_inserts.append({'idIterativeSearchRun': row.idTideIterativeRun, 'IterativeSearchRunName': row.TideRunName, 'searchType': 'tide'})
    op.bulk_insert(iterative_search_run, iterative_search_run_inserts)
    print('assigned new IDs to MSGFPlusIterativeRun')
    for row in list(connection.execute(sa.select([msgf_iterative_run_mgf_association]))):
        print(row)
        new_row = {'iterativerun_id': row.msgfiterativerun_id, 'mgf_id': row.mgf_id}
        iterative_run_mgf_association_inserts.append(new_row)
    for row in connection.execute(sa.select([tide_iterative_run_mgf_association])):
        new_row = {'iterativerun_id': row.tideiterativerun_id, 'mgf_id': row.mgf_id}
        iterative_run_mgf_association_inserts.append(new_row)
    print('going to insert into iterative_run_mgf_association')
    """
    Merge MSGFPlusIterativeRunMGFAssociation and TideIterativeRunMGFAssociation into IterativeRunMGFAssociation
    """
    iterative_run_mgf_association = sa.Table('IterativeRunMGFAssociation', metadata, sa.Column('iterativerun_id', sa.Integer, sa.ForeignKey('IterativeSearchRun.idIterativeSearchRun'), primary_key=True), sa.Column('mgf_id', sa.Integer, sa.ForeignKey('MGFfile.idMGFfile'), primary_key=True))
    op.bulk_insert(iterative_run_mgf_association, iterative_run_mgf_association_inserts)

    
    iterative_filtered_search_association = sa.Table('IterativeFilteredSearchAssociation', metadata, sa.Column('iterative_id', sa.Integer, sa.ForeignKey('IterativeSearchRun.idIterativeSearchRun'), primary_key=True), sa.Column('filteredsearch_id', sa.Integer, sa.ForeignKey('FilteredSearchResult.idFilteredSearchResult'), primary_key=True), sa.Column('step', sa.Integer))
    
    print('going to collect iterative_filtered_search_association_inserts')
    for row in list(connection.execute(sa.select([msgf_iterative_run_filteredsearch_association]))):
        new_row = {'iterative_id': row.msgfplusiterative_id, 'filteredsearch_id': row.filteredsearch_id, 'step': row.step}
        iterative_filtered_search_association_inserts.append(new_row)
    for row in list(connection.execute(sa.select([tide_iterative_filteredsearch_association]))):
        new_row = {'iterative_id': row.tideiterative_id, 'filteredsearch_id': row.filteredsearch_id, 'step': row.step}
        iterative_filtered_search_association_inserts.append(new_row)
    print('going to insert into iterative_filtered_search_association')
    op.bulk_insert(iterative_filtered_search_association, iterative_filtered_search_association_inserts)
    
    
    """
    Create IterativeRunSearchAssociation. This links IterativeSearchRun with the searches in it.
    """
    iterative_run_search_association = sa.Table('IterativeRunSearchAssociation', metadata, sa.Column('iterativerun_id', sa.Integer, sa.ForeignKey('IterativeSearchRun.idIterativeSearchRun'), primary_key=True), sa.Column('search_id', sa.Integer, sa.ForeignKey('SearchBase.idSearch'), primary_key=True))

    print('going to insert into iterative_run_search_association')
    for row in list(connection.execute(sa.select([msgf_iterative_run_filteredsearch_association]))):
        iterative_id = row.msgfplusiterative_id
        filtered_id = row.filteredsearch_id
        filtered_row = session.query(FilteredSearchResult).filter_by(idFilteredSearchResult = filtered_id).first()
        assert(filtered_row)
        qvalue_row = filtered_row.QValue
        search_row = qvalue_row.searchbase
        iterative_run_search_association_inserts.append({'iterativerun_id': iterative_id, 'search_id': search_row.idSearch})
    for row in list(connection.execute(sa.select([tide_iterative_filteredsearch_association]))):
        iterative_id = row.tideiterative_id
        filtered_id = row.filteredsearch_id
        filtered_row = session.query(FilteredSearchResult).filter_by(idFilteredSearchResult = filtered_id).first()
        assert(filtered_row)
        qvalue_row = filtered_row.QValue
        search_row = qvalue_row.searchbase
        iterative_run_search_association_inserts.append({'iterativerun_id': iterative_id, 'search_id': search_row.idSearch})
    
    op.bulk_insert(iterative_run_search_association, iterative_run_search_association_inserts)
    session.commit()
    op.drop_table('MSGFPlusIterativeRunMGFAssociation')
    op.drop_table('TideIterativeRunMGFAssociation')
    op.drop_table('TideIterativeFilteredSearchAssociation')
    op.drop_table('MSGFPlusIterativeFilteredSearchAssociation')
    with op.batch_alter_table('AssignConfidence', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_assignconfidence', 'AssignConfidenceParameterFile', ['idParameterFile'], ['idAssignConfidenceParameterFile'])

    with op.batch_alter_table('MSGFPlusIterativeRun', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_iterativerunmsgf', 'IterativeSearchRun', ['idIterativeSearchRun'], ['idIterativeSearchRun'])
        batch_op.drop_column('idMSGFPlusIterativeRun')
        batch_op.drop_column('MSGFPlusIterativeRunName')

    with op.batch_alter_table('TideIterativeRun', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_iterativeruntide', 'IterativeSearchRun', ['idIterativeSearchRun'], ['idIterativeSearchRun'])
        batch_op.drop_column('idTideIterativeRun')
        batch_op.drop_column('TideRunName')
    
    # ### end Alembic commands ###


def downgrade():
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('TideIterativeRun', schema=None) as batch_op:
        batch_op.add_column(sa.Column('TideRunName', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('idTideIterativeRun', sa.INTEGER(), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('idIterativeSearchRun')

    with op.batch_alter_table('MSGFPlusIterativeRun', schema=None) as batch_op:
        batch_op.add_column(sa.Column('MSGFPlusIterativeRunName', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('idMSGFPlusIterativeRun', sa.INTEGER(), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('idIterativeSearchRun')

    with op.batch_alter_table('AssignConfidence', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    op.create_table('MSGFPlusIterativeFilteredSearchAssociation',
    sa.Column('msgfplusiterative_id', sa.INTEGER(), nullable=False),
    sa.Column('filteredsearch_id', sa.INTEGER(), nullable=False),
    sa.Column('step', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['filteredsearch_id'], ['FilteredSearchResult.idFilteredSearchResult'], ),
    sa.ForeignKeyConstraint(['msgfplusiterative_id'], ['MSGFPlusIterativeRun.idMSGFPlusIterativeRun'], ),
    sa.PrimaryKeyConstraint('msgfplusiterative_id', 'filteredsearch_id')
    )
    op.create_table('TideIterativeFilteredSearchAssociation',
    sa.Column('tideiterative_id', sa.INTEGER(), nullable=False),
    sa.Column('filteredsearch_id', sa.INTEGER(), nullable=False),
    sa.Column('step', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['filteredsearch_id'], ['FilteredSearchResult.idFilteredSearchResult'], ),
    sa.ForeignKeyConstraint(['tideiterative_id'], ['TideIterativeRun.idTideIterativeRun'], ),
    sa.PrimaryKeyConstraint('tideiterative_id', 'filteredsearch_id')
    )
    op.create_table('TideIterativeRunMGFAssociation',
    sa.Column('tideiterativerun_id', sa.INTEGER(), nullable=False),
    sa.Column('mgf_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['mgf_id'], ['MGFfile.idMGFfile'], ),
    sa.ForeignKeyConstraint(['tideiterativerun_id'], ['TideIterativeRun.idTideIterativeRun'], ),
    sa.PrimaryKeyConstraint('tideiterativerun_id', 'mgf_id')
    )
    op.create_table('MSGFPlusIterativeRunMGFAssociation',
    sa.Column('msgfiterativerun_id', sa.INTEGER(), nullable=False),
    sa.Column('mgf_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['mgf_id'], ['MGFfile.idMGFfile'], ),
    sa.ForeignKeyConstraint(['msgfiterativerun_id'], ['MSGFPlusIterativeRun.idMSGFPlusIterativeRun'], ),
    sa.PrimaryKeyConstraint('msgfiterativerun_id', 'mgf_id')
    )
    op.drop_table('IterativeFilteredSearchAssociation')
    op.drop_table('IterativeRunSearchAssociation')
    op.drop_table('IterativeRunMGFAssociation')
    op.drop_table('IterativeSearchRun')
"""
    # ### end Alembic commands ###
