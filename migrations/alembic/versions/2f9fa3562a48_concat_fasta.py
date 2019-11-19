"""Concat FASTA

Revision ID: 2f9fa3562a48
Revises: 98735d71cdbe
Create Date: 2019-11-19 11:17:07.380135

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f9fa3562a48'
down_revision = '98735d71cdbe'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('concatfasta_to_parents',
                    sa.Column('fasta_id', sa.Integer, primary_key=True),
                    sa.Column('parent_id', sa.Integer, primary_key=True)
                    )



def downgrade():
    op.drop_table('concatfasta_to_parents')
