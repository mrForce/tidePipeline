"""MSGF+ Training

Revision ID: 98735d71cdbe
Revises: ba84174a3f83
Create Date: 2019-01-23 09:18:16.933486

"""
from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision = '98735d71cdbe'
down_revision = 'ba84174a3f83'
branch_labels = None
depends_on = None

def get_int_input(message, choices):
    while True:
        i = int(input(message))
        if i in choices:
            return i


def upgrade():
    project_location = os.getenv('PIPELINE_PROJECT', '')
    param_folder_location = os.path.join(project_location, 'msgf_params')
    if not os.path.isdir(param_folder_location):
        os.mkdir(os.path.join(project_location, 'msgf_params'))

    try:
    # ### commands auto generated by Alembic - please adjust! ###
        op.create_table('MSGFPlusTrainingParams',
                        sa.Column('idMSGFPlusTrainingParams', sa.Integer(), nullable=False),
                        sa.Column('trainingName', sa.String(), nullable=False),
                        sa.Column('paramFileLocation', sa.String(), nullable=False),
                        sa.Column('idMSGFPlusSearch', sa.Integer(), nullable=True),
                        sa.Column('idMGF', sa.Integer(), nullable=True),
                        sa.Column('fragmentationMethod', sa.Integer(), nullable=False),
                        sa.Column('instrument', sa.Integer(), nullable=False),
                        sa.Column('enzyme', sa.Integer(), nullable=False),
                        sa.ForeignKeyConstraint(['idMGF'], ['MGFfile.idMGFfile'], ),
                        sa.ForeignKeyConstraint(['idMSGFPlusSearch'], ['MSGFPlusSearch.idSearch'], ),
                        sa.PrimaryKeyConstraint('idMSGFPlusTrainingParams'),
                        sa.UniqueConstraint('paramFileLocation'),
                        sa.UniqueConstraint('trainingName')
        )
    except:
        print('error in creating table')        

    with op.batch_alter_table('MGFfile', schema=None) as batch_op:
        try:
            batch_op.add_column(sa.Column('enzyme', sa.Integer(), nullable=True))
        except:
            print('Error in adding enzyme column')
        try:
            batch_op.add_column(sa.Column('fragmentationMethod', sa.Integer(), nullable=True))
        except:
            print('Error in adding fragmentationMethod column')
        try:
            batch_op.add_column(sa.Column('instrument', sa.Integer(), nullable=True))
        except:
            print('error in adding instrument column')

    with op.batch_alter_table('MSGFPlusSearch', schema=None) as batch_op:
        try:
            batch_op.add_column(sa.Column('idMSGFPlusTrainingParams', sa.Integer(), nullable=True))
        except:
            print('error in adding idMSGFPlusTrainingParams column')
        try:            
            batch_op.create_foreign_key('idMSGFPlusTrainingParams', 'MSGFPlusTrainingParams', ['idMSGFPlusTrainingParams'], ['idMSGFPlusTrainingParams'])
        except:
            print('Error in adding idMSGFPlusTrainingParams foreign key')

    metadata = sa.MetaData()
    connection = op.get_bind()
    """
    Now we need to prompt the user to assign fragmentationMethod, instrument and enzyme to each MGFfile
    """
    mgfFile = sa.Table('MGFfile', metadata, sa.Column('idMGFfile', sa.Integer, primary_key=True), sa.Column('MGFName', sa.String, unique=True), sa.Column('enzyme', sa.Integer), sa.Column('fragmentationMethod', sa.Integer), sa.Column('instrument', sa.Integer))
    for row in list(connection.execute(sa.select([mgfFile]))):
        print('MGF file: ' + row.MGFName)
        fragmentation = get_int_input('Set the fragmentation method: 0 is CID, 1 is ETD, 2 is HCD. ', [0, 1, 2])
        instrument = get_int_input('Instrument? 0 is low-res LCQ/LTQ, 1 is High-Req LTQ, 2 is TOF, 3 is Q-Extractive. ', [0, 1, 2, 3])
        enzyme = get_int_input('0 is Trypsin, 1 is Chymotrypsin, 2 is Lys-C, 3 is Lys-N, 4 is glutamyl endopeptidase, 5 is Arg-C, 6 is Asp-N, 7 is alphaLP, 8 is no cleavage', [0, 1, 2, 3, 4, 5, 6, 7, 8])
        connection.execute(mgfFile.update().where(mgfFile.c.idMGFfile == row.idMGFfile).values(enzyme=enzyme, fragmentationMethod=fragmentation, instrument=instrument))
        
        
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('MSGFPlusSearch', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('idMSGFPlusSearch')

    with op.batch_alter_table('MGFfile', schema=None) as batch_op:
        batch_op.drop_column('instrument')
        batch_op.drop_column('fragmentationMethod')
        batch_op.drop_column('enzyme')

    op.drop_table('MSGFPlusTrainingParams')

    # ### end Alembic commands ###
