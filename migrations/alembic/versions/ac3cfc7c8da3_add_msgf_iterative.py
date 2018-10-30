"""Add MSGF+ iterative

Revision ID: ac3cfc7c8da3
Revises: 73d61148091e
Create Date: 2018-07-23 13:08:44.036533

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac3cfc7c8da3'
down_revision = '73d61148091e'
branch_labels = None
depends_on = None


def upgrade():
    #op.create_table('MSGFPlusIterativeRun', sa.Column('idMSGFPlusIterativeRun', sa.Integer, primary_key=True), sa.Column('MSGFPlusIterativeRunName', sa.String, unique=True), sa.Column('fdr', sa.String), sa.Column('num_steps', sa.Integer), sa.Column('idMGF', sa.Integer, sa.ForeignKey('MGFfile.idMGFfile')))
    op.create_table('MSGFPlusIterativeFilteredSearchAssociation', sa.Column('msgfplusiterative_id', sa.Integer, sa.ForeignKey('MSGFPlusIterativeRun.idMSGFPlusIterativeRun'), primary_key=True), sa.Column('filteredsearch_id', sa.Integer, sa.ForeignKey('FilteredSearchResult.idFilteredSearchResult'), primary_key=True), sa.Column('step', sa.Integer))



def downgrade():
    pass
