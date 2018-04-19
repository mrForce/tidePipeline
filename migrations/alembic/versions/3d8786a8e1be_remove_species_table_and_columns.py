"""remove species table and columns

Revision ID: 3d8786a8e1be
Revises: 
Create Date: 2018-04-17 15:43:41.026272

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, create_engine, Float, BLOB, DateTime

from sqlalchemy.orm import relationship


# revision identifiers, used by Alembic.
revision = '3d8786a8e1be'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('HLA') as batch_op:
        batch_op.drop_column('species_id')
    op.drop_table('Species')
    pass


def downgrade():
    op.create_table('Species', Column('idSpecies', Integer, primary_key=True),
                    Column('SpeciesName', String, unique=True),
                    hlas= relationship('HLA', back_populates='species'))
    with op.batch_alter_table('HLA') as batch_op:
        batch_op.add_column('species_id', sa.Column('species_id', ForeignKey('Species.idSpecies')))
    pass
