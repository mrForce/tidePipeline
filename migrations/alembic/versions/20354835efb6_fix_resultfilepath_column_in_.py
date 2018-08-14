"""Fix resultFilePath column in MSGFPlusSearch

Revision ID: 20354835efb6
Revises: ebf98eb0c77e
Create Date: 2018-08-14 11:27:36.766011

"""
from alembic import op
import sqlalchemy as sa
from pathlib import Path
import os
# revision identifiers, used by Alembic.
revision = '20354835efb6'
down_revision = 'ebf98eb0c77e'
branch_labels = None
depends_on = None


def upgrade():
    project_location = os.getenv('PIPELINE_PROJECT', '')
    print('project location')
    print(project_location)
    assert(len(project_location) > 0)
    parts = Path(project_location).parts
    end_part = parts[-1]
    # ### commands auto generated by Alembic - please adjust! ###
    connection = op.get_bind()

    metadata = sa.MetaData()


    msgfplussearch = sa.Table('MSGFPlusSearch', metadata, sa.Column('idSearch', sa.Integer, sa.ForeignKey('SearchBase.idSearch'), primary_key=True), sa.Column('resultFilePath', sa.String))
    for row in connection.execute(sa.select([msgfplussearch])):
        result_path = row.resultFilePath
        result_path_parts = Path(result_path).parts
        if result_path_parts[0] == end_part:
            needed_parts = result_path_parts[1::]
            new_path = Path(*needed_parts)            
            update = msgfplussearch.update().where(msgfplussearch.c.idSearch == row.idSearch).values(resultFilePath=str(new_path))
            print('going to replace: ' + row.resultFilePath + ' with: ' + str(new_path))
            connection.execute(update)
        else:
            print('No need to replace: ' + row.resultFilePath)
    with op.batch_alter_table('AssignConfidence') as batch_op:
        batch_op.create_foreign_key('idParameterFile', 'AssignConfidenceParameterFile', ['idParemeterFile'], ['idAssignConfidenceParameterFile'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'AssignConfidence', type_='foreignkey')
    # ### end Alembic commands ###