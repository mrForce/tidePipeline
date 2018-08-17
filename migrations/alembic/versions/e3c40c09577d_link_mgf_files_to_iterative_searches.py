"""link MGF files to iterative searches

Revision ID: e3c40c09577d
Revises: 20354835efb6
Create Date: 2018-08-16 13:18:50.709632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3c40c09577d'
down_revision = '20354835efb6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    
    op.create_table('MSGFPlusIterativeRunMGFAssociation',
    sa.Column('msgfiterativerun_id', sa.Integer(), nullable=False),
    sa.Column('mgf_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['mgf_id'], ['MGFfile.idMGFfile'], ),
    sa.ForeignKeyConstraint(['msgfiterativerun_id'], ['MSGFPlusIterativeRun.idMSGFPlusIterativeRun'], ),
    sa.PrimaryKeyConstraint('msgfiterativerun_id', 'mgf_id')
    )
    op.create_table('TideIterativeRunMGFAssociation',
    sa.Column('tideiterativerun_id', sa.Integer(), nullable=False),
    sa.Column('mgf_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['mgf_id'], ['MGFfile.idMGFfile'], ),
    sa.ForeignKeyConstraint(['tideiterativerun_id'], ['TideIterativeRun.idTideIterativeRun'], ),
    sa.PrimaryKeyConstraint('tideiterativerun_id', 'mgf_id')
    )
    with op.batch_alter_table('AssignConfidence') as batch_op:
        batch_op.create_foreign_key('idParameterFile', 'AssignConfidenceParameterFile', ['idParemeterFile'], ['idAssignConfidenceParameterFile'])
    metadata = sa.MetaData()
    connection = op.get_bind()

    
    mgfFile = sa.Table('MGFfile', metadata, sa.Column('idMGFfile', sa.Integer, primary_key=True), sa.Column('MGFName', sa.String, unique=True), sa.Column('partOfIterativeSearch', sa.Boolean, default=False))
    searchbase = sa.Table('SearchBase', metadata, sa.Column('idSearch', sa.Integer, primary_key=True), sa.Column('partOfIterativeSearch', sa.Boolean), sa.Column('SearchName', sa.String, unique=True))
    tidesearch = sa.Table('TideSearch', metadata, sa.Column('idSearch', sa.Integer, sa.ForeignKey('SearchBase.idSearch'), primary_key=True), sa.Column('idMGF', sa.Integer, sa.ForeignKey('MGFfile.idMGFfile')))
    msgfsearch = sa.Table('MSGFPlusSearch', metadata, sa.Column('idSearch', sa.Integer, sa.ForeignKey('SearchBase.idSearch'), primary_key=True), sa.Column('idMGF', sa.Integer, sa.ForeignKey('MGFfile.idMGFfile')))
    qvaluebase = sa.Table('QValueBase', metadata, sa.Column('idQValue', sa.Integer, primary_key=True), sa.Column('idSearchBase', sa.Integer, sa.ForeignKey('SearchBase.idSearch')), sa.Column('partOfIterativeSearch', sa.Boolean))
    filteredsearch_result = sa.Table('FilteredSearchResult', metadata, sa.Column('idFilteredSearchResult', sa.Integer, primary_key=True), sa.Column('filteredSearchResultName', sa.String, unique=True), sa.Column('idQValueBase', sa.Integer, sa.ForeignKey('QValueBase.idQValue')), sa.Column('partOfIterativeSearch', sa.Boolean), sa.Column('idQValueBase', sa.Integer, sa.ForeignKey('QValueBase.idQValue')))
    msgf_iterative_run = sa.Table('MSGFPlusIterativeRun', metadata, sa.Column('idMSGFPlusIterativeRun', sa.Integer, primary_key=True), sa.Column('MSGFPlusIterativeRunName', sa.String))
    tide_iterative_run = sa.Table('TideIterativeRun', metadata, sa.Column('idTideIterativeRun', sa.Integer, primary_key=True), sa.Column('TideRunName', sa.String))

    tide_iterative_filtered_search_association= sa.Table('TideIterativeFilteredSearchAssociation', metadata, sa.Column('tideiterative_id', sa.Integer, sa.ForeignKey('TideIterativeRun.idTideIterativeRun'), primary_key=True), sa.Column('filteredsearch_id', sa.Integer, sa.ForeignKey('FilteredSearchResult.idFilteredSearchResult'), primary_key=True))
    msgf_iterative_filtered_search_association= sa.Table('MSGFPlusIterativeFilteredSearchAssociation', metadata, sa.Column('msgfplusiterative_id', sa.Integer, sa.ForeignKey('MSGFPlusIterativeRun.idMSGFPlusIterativeRun'), primary_key=True), sa.Column('filteredsearch_id', sa.Integer, sa.ForeignKey('FilteredSearchResult.idFilteredSearchResult'), primary_key=True))
    msgf_iterative_mgf_association = sa.Table('MSGFPlusIterativeRunMGFAssociation', metadata, sa.Column('msgfiterativerun_id', sa.Integer, sa.ForeignKey('MSGFPlusIterativeRun.idMSGFPlusIterativeRun'), primary_key=True), sa.Column('mgf_id', sa.Integer, sa.ForeignKey('MGFfile.idMGFfile'), primary_key=True))
    tide_iterative_mgf_association = sa.Table('TideIterativeRunMGFAssociation', metadata, sa.Column('tideiterativerun_id', sa.Integer, sa.ForeignKey('TideIterativeRun.idTideIterativeRun'), primary_key=True), sa.Column('mgf_id', sa.Integer, sa.ForeignKey('MGFfile.idMGFfile'), primary_key=True))


    for row in connection.execute(sa.select([filteredsearch_result])):
        if row.partOfIterativeSearch:
            print('row')
            #find the MGFfile that it is linked to by path FilteredSearchResult->QValueBase->SearchBase->MGF
            qvalue_list = list(connection.execute(sa.select([qvaluebase]).where(qvaluebase.c.idQValue == row.idQValueBase)))
            if len(qvalue_list) == 0:
                print("There aren't any QValueBase's associated with: " + row.filteredSearchResultName)
                continue
            elif len(qvalue_list) > 1:
                print('There are more than 1 QValueBase\'s with id: ' + str(row.idQValueBase))
                break
            else:
                qvalue = qvalue_list[0]
                searchbase_list = list(connection.execute(sa.select([searchbase]).where(searchbase.c.idSearch == qvalue.idSearchBase)))
                if len(searchbase_list) == 0:
                    print('QValueBase with ID: ' + str(qvalue.idQValue) + ' has no associated SearchBase\'s')
                    continue
                elif len(searchbase_list) > 1:
                    print('There are multiple SearchBase\'s with id: '  + str(qvalue.idSearchBase))
                    break
                else:
                    searchbase_row = searchbase_list[0]
                    search_name = searchbase_row.SearchName
                    tidesearch_rows = list(connection.execute(sa.select([tidesearch]).where(tidesearch.c.idSearch == searchbase_row.idSearch)))
                    if len(tidesearch_rows) > 1:
                        print('More than 1 rows in TideSearch with id: ' + str(searchbase_row.idSearch))
                        break
                    elif len(tidesearch_rows) == 1:
                        tidesearch_row = tidesearch_rows[0]
                        mgf_rows = list(connection.execute(sa.select([mgfFile]).where(mgfFile.c.idMGFfile == tidesearch_row.idMGF)))
                        if len(mgf_rows) == 0:
                            print('the Tide search: ' + search_name + ' is associated with the  MGF file with id: ' + str(tidesearch_row.idMGF) + ' but there is no row in the MGFfile table with that ID')
                            continue
                        elif len(mgf_rows) > 1:
                            print('More than 1 MGFfile row with id: ' + str(tidesearch_row.idMGF))
                            break
                        else:
                            mgf_row = mgf_rows[0]
                            association_rows = list(connection.execute(sa.select([tide_iterative_filtered_search_association]).where(tide_iterative_filtered_search_association.c.filteredsearch_id == row.idFilteredSearchResult)))
                            if len(association_rows) == 0:
                                print('Skipping FilteredSearchResult, since it isn\'t associated with a Tide iterative search')
                                continue
                            elif len(association_rows) == 1:
                                association_row = association_rows[0]
                                tide_iterative_search_rows = list(connection.execute(sa.select([tide_iterative_run]).where(tide_iterative_run.c.idTideIterativeRun == association_row.tideiterative_id)))
                                if len(tide_iterative_search_rows) == 0:
                                    print('There is no Tide Iterative search run with ID: ' + str(association_row.tideiterative_id))
                                    continue
                                elif len(tide_iterative_search_rows) == 1:
                                    tide_iterative_search_row = tide_iterative_search_rows[0]
                                    #now link via  TideIterativeRunMGFAssociation
                                    print('Linking tide iterative run: ' + tide_iterative_search_row.TideRunName + ' with MGF: '  + mgf_row.MGFName)
                                    op.bulk_insert(tide_iterative_mgf_association, [{'tideiterativerun_id': tide_iterative_search_row.idTideIterativeRun, 'mgf_id': mgf_row.idMGFfile}])
                                else:
                                    print('Multiple Tide iterative search rows with same ID: ' + str(association_row.tideiterative_id))
                                    break
                            else:
                                print('Multiple rows in TideIterativeFilteredSearchAssociation table where filteredsearch_id is: ' + str(row.idFilteredSearchResult))
                                break
                    elif len(tidesearch_rows) == 0:
                        msgfsearch_rows = list(connection.execute(sa.select([msgfsearch]).where(msgfsearch.c.idSearch == searchbase_row.idSearch)))
                        if len(msgfsearch_rows) == 0:
                            print('SearchBase with ID: ' + str(searchbase_row.idSearch) + ' has no corresponding MSGF+ or Tide search')
                            continue
                        elif len(msgfsearch_rows) > 1:
                            print('More than 1 MGFPlusSearch row with id: ' + str(searchbase_row.idSearch))
                            break
                        elif len(msgfsearch_rows) == 1:
                            msgfsearch_row = msgfsearch_rows[0]
                            mgf_rows = list(connection.execute(sa.select([mgfFile]).where(mgfFile.c.idMGFfile == msgfsearch_row.idMGF)))
                            if len(mgf_rows) == 0:
                                print('the MSGF search: ' + search_name + ' is associated with the  MGF file with id: ' + str(msgfsearch_row.idMGF) + ' but there is no row in the MGFfile table with that ID')
                                continue
                            elif len(mgf_rows) > 1:
                                print('More than 1 MGFfile row with id: ' + str(msgfsearch_row.idMGF))
                                break
                            else:
                                mgf_row = mgf_rows[0]
                                association_rows = list(connection.execute(sa.select([msgf_iterative_filtered_search_association]).where(msgf_iterative_filtered_search_association.c.filteredsearch_id == row.idFilteredSearchResult)))
                                if len(association_rows) == 0:
                                    print('Skipping FilteredSearchResult, since it isn\'t associated with an MSGF+ iterative search')
                                    continue
                                elif len(association_rows) == 1:
                                    association_row = association_rows[0]
                                    msgf_iterative_search_rows = list(connection.execute(sa.select([msgf_iterative_run]).where(msgf_iterative_run.c.idMSGFPlusIterativeRun == association_row.msgfplusiterative_id)))
                                    if len(msgf_iterative_search_rows) == 0:
                                        print('There is no MSGF+ Iterative search run with ID: ' + str(association_row.msgfplusiterative_id))
                                        continue
                                    elif len(msgf_iterative_search_rows) == 1:
                                        msgf_iterative_search_row = msgf_iterative_search_rows[0]
                                        print('linking MSGF+ Iterative search: ' + msgf_iterative_search_row.MSGFPlusIterativeRunName + ' with MGF: ' + mgf_row.MGFName)
                                        #now link via  MSGFPlusIterativeRunMGFAssociation
                                        op.bulk_insert(msgf_iterative_mgf_association, [{'msgfiterativerun_id': msgf_iterative_search_row.idMSGFPlusIterativeRun, 'mgf_id': mgf_row.idMGFfile}])
                                    else:
                                        print('Multiple MSGF+ iterative search rows with same ID: ' + str(association_row.msgfplusiterative_id))
                                        break
                                else:
                                    print('Multiple rows in MSGFPlusIterativeFilteredSearchAssociation table where filteredsearch_id is: ' + str(row.idFilteredSearchResult))
                                    break
                                              
                    
                    


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'AssignConfidence', type_='foreignkey')
    op.drop_table('TideIterativeRunMGFAssociation')
    op.drop_table('MSGFPlusIterativeRunMGFAssociation')
    # ### end Alembic commands ###