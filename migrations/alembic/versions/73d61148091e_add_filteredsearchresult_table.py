"""Add FilteredSearchResult table

Revision ID: 73d61148091e
Revises: 8d70dec8ab88
Create Date: 2018-04-23 14:59:14.107144

"""
from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision = '73d61148091e'
down_revision = '8d70dec8ab88'
branch_labels = None
depends_on = None


def upgrade():
    project_location = os.getenv('PIPELINE_PROJECT', '')
    assert(len(project_location) > 0)
    if not os.path.isdir(os.path.join(project_location, 'FilteredSearchResult')):
        os.mkdir(os.path.join(project_location, 'FilteredSearchResult'))
    metadata = sa.MetaData()

    op.create_table('FilteredSearchResult', sa.Column('idFilteredSearchResult', sa.Integer, primary_key=True), sa.Column('filteredSearchResultName', sa.String, unique=True), sa.Column('filteredSearchResultPath', sa.String), sa.Column('q_value_threshold', sa.Float), sa.Column('method', sa.String))
    


def downgrade():
    pass
