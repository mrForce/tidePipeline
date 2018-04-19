"""Add column for location of filtered peptides in FilteredNetMHC table

Revision ID: fc96a191e85a
Revises: 3d8786a8e1be
Create Date: 2018-04-18 14:13:21.603409

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import relationship
import os
import uuid
import shutil
# revision identifiers, used by Alembic.
revision = 'fc96a191e85a'
down_revision = '3d8786a8e1be'
branch_labels = None
depends_on = None


def extract_peptides(input_file_path, output_file_path, threshold):
    with open(input_file_path, 'r') as f:
        with open(output_file_path, 'w') as g:
            for line in f:
                parts = line.split(',')
                if len(parts) == 2:
                    peptide = parts[0]
                    rank = float(parts[1])
                    if rank <= threshold:
                        g.write(peptide + '\n')
                else:
                    print('Could not parse line: ' + line)

def upgrade():
    project_location = os.getenv('PIPELINE_PROJECT', '')
    print('project location')
    print(project_location)
    assert(len(project_location) > 0)
    if not os.path.isdir(os.path.join(project_location, 'FilteredNetMHC')):
        os.mkdir(os.path.join(project_location, 'FilteredNetMHC'))
    with op.batch_alter_table('FilteredNetMHC') as batch_op:
        batch_op.add_column(sa.Column('filtered_path', sa.String))
        batch_op.add_column(sa.Column('FilteredNetMHCName', sa.String))
    connection = op.get_bind()

    metadata = sa.MetaData()
    hla = sa.Table('HLA', metadata, sa.Column('idHLA', sa.Integer, primary_key=True), sa.Column('HLAName', sa.String))
    peptide_list = sa.Table('PeptideList', metadata, sa.Column('idPeptideList', sa.Integer, primary_key=True), sa.Column('peptideListName', sa.String, unique=True))
    filtered = sa.Table('FilteredNetMHC',metadata, sa.Column('idFilteredNetMHC', sa.Integer, primary_key=True), sa.Column('idNetMHC', sa.Integer, sa.ForeignKey('NetMHC.idNetMHC')), sa.Column('RankCutoff', sa.Float), sa.Column('filtered_path', sa.String), sa.Column('FilteredNetMHCName', sa.String, unique=True))
    netmhc = sa.Table('NetMHC', metadata, sa.Column('idNetMHC', sa.Integer, primary_key = True), sa.Column('idHLA', sa.Integer), sa.Column('HighScoringPeptidesPath', sa.String), sa.Column('peptideListID', sa.Integer))
    updates = list()
    for row in connection.execute(sa.select([peptide_list, filtered, netmhc, hla]).where(filtered.c.idNetMHC == netmhc.c.idNetMHC).where(netmhc.c.peptideListID == peptide_list.c.idPeptideList).where(netmhc.c.idHLA == hla.c.idHLA)):
        print('row')
        path = os.path.join(project_location, row.HighScoringPeptidesPath)
        file_name = str(uuid.uuid4())
        while os.path.isfile(os.path.join(project_location, 'FilteredNetMHC', file_name)):
            file_name = str(uuid.uuid4())
        output_path = os.path.join(project_location, 'FilteredNetMHC', file_name)
        extract_peptides(path, output_path, row.RankCutoff)
        print('row')
        print(row)
        print('row in filtered')

        print('peptide list name')
        print(row.peptideListName)
        print('hla name')
        print(row.HLAName)
        update = filtered.update().where(filtered.c.idFilteredNetMHC == row.idFilteredNetMHC).values(filtered_path=os.path.join('FilteredNetMHC', file_name), FilteredNetMHCName = row.peptideListName + '_' + str(row.RankCutoff) + '_' + row.HLAName)

        updates.append(update)


    for pu in updates:
        print('going to do path update')
        print(pu)
        connection.execute(pu)

        

    
        


def downgrade():
    #with op.batch_alter_table('FilteredNetMHC') as batch_op:
    #    batch_op.drop_column('filtered_path')
    project_location = os.getenv('PIPELINE_PROJECT', '')
    print('project location')
    print(project_location)
    assert(len(project_location) > 0)
    if os.path.isdir(os.path.join(project_location, 'FilteredNetMHC')):
        shutil.rmtree(os.path.join(project_location, 'FilteredNetMHC'))

