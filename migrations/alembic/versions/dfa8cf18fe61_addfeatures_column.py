"""addFeatures column

Revision ID: dfa8cf18fe61
Revises: ac3cfc7c8da3
Create Date: 2018-08-06 15:46:41.809131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfa8cf18fe61'
down_revision = 'ac3cfc7c8da3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('MSGFPlusSearch', Column('addFeatures', sa.Integer), server_default = 0, nullable=False)


def downgrade():
    op.drop_column('MSGFPlusSearch', 'addFeatures')
