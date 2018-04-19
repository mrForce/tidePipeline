"""Create a TargetSet table.

Revision ID: 8d70dec8ab88
Revises: fc96a191e85a
Create Date: 2018-04-19 14:21:17.046809

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import relationship
import os

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
    op.create_table('TargetSet', sa.Column('idTargetSet', sa.Integer, primary_key=True), sa.Column('TargetSetFASTAPath', sa.String, unique=True), sa.Column('PeptideSourceMapPath', sa.String), sa.Column('SourceSymbolMap', sa.String))
    op.create_table('tideindex_targetset',  sa.Column('tideindex_id', sa.ForeignKey('TideIndex.idTideIndex'), primary_key = True), sa.Column('targetset_id', sa.ForeignKey('TargetSet.idTargetSet'), primary_key=True))
    op.create_table('targetset_filteredNetMHC', sa.Column('targetset_id', sa.ForeignKey('TargetSet.idTargetSet'), primary_key = True), sa.Column('filteredNetMHC_id', sa.ForeignKey('FilteredNetMHC.idFilteredNetMHC'), primary_key=True))
    

def downgrade():
    pass
