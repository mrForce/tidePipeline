"""Create a TargetSet table.

Revision ID: 8d70dec8ab88
Revises: fc96a191e85a
Create Date: 2018-04-19 14:21:17.046809

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import relationship
import os
from collections import defaultdict
import json
import uuid
def create_target_set(filtered_netmhc, peptide_lists, output_fasta_location, output_json_location):
    assert(not os.path.isfile(output_fasta_location))
    assert(not os.path.isdir(output_fasta_location))
    assert(not os.path.isfile(output_json_location))
    assert(not os.path.isdir(output_json_location))

    with open(output_fasta_location, 'w') as f:
        pass
    with open(output_json_location, 'w') as f:
        pass
    i = 0
    filtered_map = {}
    filtered_map_reverse = {}
    for name, location in filtered_netmhc:
        filtered_map[i] = name
        filtered_map_reverse[name] = i
        i += 1
    peptide_lists_map = {}
    peptide_lists_map_reverse = {}
    for name, location in peptide_lists:
        peptide_lists_map[i] = name
        peptide_lists_map_reverse[name] = i
        i += 1
    source_id_map = {'filtered_netmhc': filtered_map, 'peptide_lists': peptide_lists_map}
    target_set = defaultdict(list)
    for name, location in filtered_netmhc:
        source_id = filtered_map_reverse[name]
        with open(location, 'r') as f:
            for line in f:
                if len(line.strip()) > 0:
                    target_set[line.strip()].append(source_id)
    for name, location in peptide_lists:
        source_id = peptide_lists_map_reverse[name]
        with open(location, 'r') as f:
            for line in f:
                if len(line.strip()) > 0:
                    target_set[line.strip()].append(source_id)
    i = 0
    with open(output_fasta_location, 'w') as f:
        for target_sequence, source_list in target_set.items():
            assert(len(source_list) > 0)
            f.write('>' + str(i) + '\n')
            f.write(target_sequence + '\n')
            if len(source_list) == 1:
                target_set[target_sequence] = source_list[0]
            i += 1
    with open(output_json_location, 'w') as g:
        json.dump(dict(target_set), g)
    return source_id_map

# revision identifiers, used by Alembic.
revision = '8d70dec8ab88'
down_revision = 'fc96a191e85a'
branch_labels = None
depends_on = None






def upgrade():
    """
    First, we need to add a directory for target sets
    """
    project_location = os.getenv('PIPELINE_PROJECT', '')
    assert(len(project_location) > 0)
    if not os.path.isdir(os.path.join(project_location, 'TargetSet')):
        os.mkdir(os.path.join(project_location, 'TargetSet'))
    metadata = sa.MetaData()
    op.create_table('TargetSet', sa.Column('idTargetSet', sa.Integer, primary_key=True), sa.Column('TargetSetFASTAPath', sa.String, unique=True), sa.Column('PeptideSourceMapPath', sa.String), sa.Column('SourceIDMap', sa.String))
    op.create_table('tideindex_targetset',  sa.Column('tideindex_id', sa.Integer, sa.ForeignKey('TideIndex.idTideIndex'), primary_key = True), sa.Column('targetset_id', sa.Integer, sa.ForeignKey('TargetSet.idTargetSet'), primary_key=True))
    op.create_table('targetset_filteredNetMHC', sa.Column('targetset_id', sa.Integer, sa.ForeignKey('TargetSet.idTargetSet'), primary_key = True), sa.Column('filteredNetMHC_id', sa.Integer, sa.ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))
    op.create_table('targetset_peptidelists', sa.Column('targetset_id', sa.Integer, sa.ForeignKey('TargetSet.idTargetSet'), primary_key = True), sa.Column('peptideList_id', sa.Integer, sa.ForeignKey('PeptideList.idPeptideList'), primary_key=True))

    target_set = sa.Table('TargetSet', metadata, sa.Column('idTargetSet', sa.Integer, primary_key = True), sa.Column('TargetSetFASTAPath', sa.String, unique=True), sa.Column('PeptideSourceMapPath', sa.String), sa.Column('SourceIDMap', sa.String))
    peptide_list = sa.Table('PeptideList', metadata, sa.Column('idPeptideList', sa.Integer, primary_key=True), sa.Column('peptideListName', sa.String, unique=True))
    filtered = sa.Table('FilteredNetMHC',metadata, sa.Column('idFilteredNetMHC', sa.Integer, primary_key=True), sa.Column('idNetMHC', sa.Integer, sa.ForeignKey('NetMHC.idNetMHC')), sa.Column('RankCutoff', sa.Float), sa.Column('filtered_path', sa.String), sa.Column('FilteredNetMHCName', sa.String, unique=True))
    #we don't need very many columns here
    tide_index = sa.Table('TideIndex', metadata, sa.Column('idTideIndex', sa.Integer, primary_key = True), sa.Column('TideIndexName', sa.String, unique=True))
    tideindex_filteredNetMHC = sa.Table('tideindex_filteredNetMHC', metadata, sa.Column('tideindex_id', sa.Integer, sa.ForeignKey('TideIndex.idTideIndex'), primary_key=True), sa.Column('filteredNetMHC_id', sa.Integer, sa.ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))

    tideindex_peptidelists = sa.Table('tideindex_peptidelists', metadata, sa.Column('tideindex_id', sa.Integer, sa.ForeignKey('TideIndex.idTideIndex'), primary_key=True), sa.Column('peptidelist_id', sa.Integer, sa.ForeignKey('PeptideList.idPeptideList'), primary_key=True))
    targetset_filteredNetMHC = sa.Table('targetset_filteredNetMHC', metadata, sa.Column('targetset_id', sa.Integer, sa.ForeignKey('TargetSet.idTargetSet'), primary_key = True), sa.Column('filteredNetMHC_id', sa.Integer, sa.ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))
    targetset_peptidelists = sa.Table('targetset_peptidelists', metadata, sa.Column('targetset_id', sa.Integer, sa.ForeignKey('TargetSet.idTargetSet'), primary_key = True), sa.Column('peptideList_id', sa.Integer, sa.ForeignKey('PeptideList.idPeptideList'), primary_key=True))
    connection = op.get_bind()

    for tide_index_row in connection.execute(sa.select([tide_index])):
        table_inserts = []
        tide_index_id = tide_index_row.idTideIndex
        filtered_netmhc_list = []
        peptide_lists = []
        for filtered_row in connection.execute(sa.select([tideindex_filteredNetMHC, filtered]).where(tideindex_filteredNetMHC.c.tideindex_id == tide_index_id).where(tideindex_filteredNetMHC.c.filteredNetMHC_id == filtered.c.idFilteredNetMHC)):
            filtered_path = filtered_row.filtered_path
            name = filtered_row.FilteredNetMHCName
            filtered_netmhc_list.append((name, os.path.join(project_location, filtered_path)))
            table_inserts.append(targetset_filteredNetMHC.insert().values(targetset_id=sa.bindparam('target_set_id'), filteredNetMHC_id = filtered_row.idFilteredNetMHC))
        for peptide_list_row in connection.execute(sa.select([tideindex_peptidelists, peptide_list]).where(tideindex_peptidelists.c.tideindex_id == tide_index_id).where(tideindex_peptidelists.c.peptidelist_id == peptide_list.c.idPeptideList)):
            peptide_list_path = peptide_list_row.PeptideListPath
            name = peptide_list_row.peptideListName
            peptide_lists.append((name, os.path.join(project_location, peptide_list_path)))
            table_inserts.append(targetset_peptidelists.insert().values(targetset_id=sa.bindparam('target_set_id'), peptideList_id = peptide_list_row.idPeptideList))
        name = str(uuid.uuid4())
        while os.path.isdir(os.path.join(project_location, 'TargetSet', name)) or os.path.isfile(os.path.join(project_location, 'TargetSet', name)):
            name = str(uuid.uuid4())
        output_directory = os.path.join(project_location, 'TargetSet', name)
        os.mkdir(output_directory)
        source_map = create_target_set(filtered_netmhc_list, peptide_lists, os.path.join(output_directory, 'targets.fasta'), os.path.join(output_directory, 'sources.json'))
        result = connection.execute(target_set.insert().values(TargetSetFASTAPath = os.path.join('TargetSet',name, 'targets.fasta'), PeptideSourceMapPath = os.path.join('TargetSet', name, 'sources.json'), SourceIDMap = json.dumps(source_map)))
        target_set_id = result.inserted_primary_key[0]
        #need to run inserts
        for insert in table_inserts:
            connection.execute(insert, {'target_set_id': target_set_id})
        
        
    
    

def downgrade():
    pass
