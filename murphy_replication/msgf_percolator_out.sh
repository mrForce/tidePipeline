#  ██████╗ ██╗██████╗     ██╗   ██╗ ██████╗ ██╗   ██╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗
#  ██╔══██╗██║██╔══██╗    ╚██╗ ██╔╝██╔═══██╗██║   ██║    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝
#  ██║  ██║██║██║  ██║     ╚████╔╝ ██║   ██║██║   ██║    ██║     ███████║█████╗  ██║     █████╔╝ 
#  ██║  ██║██║██║  ██║      ╚██╔╝  ██║   ██║██║   ██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ 
#  ██████╔╝██║██████╔╝       ██║   ╚██████╔╝╚██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗
#  ╚═════╝ ╚═╝╚═════╝        ╚═╝    ╚═════╝  ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
#      ████████╗██╗  ██╗███████╗                                                                 
#      ╚══██╔══╝██║  ██║██╔════╝                                                                 
#         ██║   ███████║█████╗                                                                   
#         ██║   ██╔══██║██╔══╝                                                                   
#         ██║   ██║  ██║███████╗                                                                 
#         ╚═╝   ╚═╝  ╚═╝╚══════╝                                                                 
#   ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗██╗     ██╗███████╗████████╗██████╗                   
#  ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██║     ██║██╔════╝╚══██╔══╝╚════██╗                  
#  ██║     ███████║█████╗  ██║     █████╔╝ ██║     ██║███████╗   ██║     ▄███╔╝                  
#  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██║     ██║╚════██║   ██║     ▀▀══╝                   
#  ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║███████║   ██║     ██╗                     
#   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝   ╚═╝     ╚═╝                     
#                                                                                                
project folder: MurphyReplication
project path: MurphyReplication
going to begin command session
going to validate project integrity
current time: 20:13:50.349830
going to check fasta rows
going to check peptide list rows
going to check mgf rows
done validating project integrity
current time: 20:13:50.372851
starting command session
got MSGF+ search runner
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlite3.OperationalError: no such column: MSGFPlusSearch.addFeatures

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "RunMSGFPlusSearch.py", line 47, in <module>
    project.run_search(args.mgf_name, args.index_name, modifications_name, search_runner, args.search_name, args.memory)
  File "/home/jordan/git/tidePipeline/MSGFPlusEngine.py", line 118, in run_search
    search_row = self.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName=search_name).first()
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2888, in first
    ret = list(self[0:1])
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2680, in __getitem__
    return list(res)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2988, in __iter__
    return self._execute_and_instances(context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 3011, in _execute_and_instances
    result = conn.execute(querycontext.statement, self._params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 948, in execute
    return meth(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/sql/elements.py", line 269, in _execute_on_connection
    return connection._execute_clauseelement(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1060, in _execute_clauseelement
    compiled_sql, distilled_params
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1200, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1413, in _handle_dbapi_exception
    exc_info
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 265, in raise_from_cause
    reraise(type(exception), exception, tb=exc_tb, cause=cause)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 248, in reraise
    raise value.with_traceback(tb)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: MSGFPlusSearch.addFeatures [SQL: 'SELECT "MSGFPlusSearch"."idSearch" AS "MSGFPlusSearch_idSearch", "SearchBase"."idSearch" AS "SearchBase_idSearch", "SearchBase"."searchType" AS "SearchBase_searchType", "SearchBase"."SearchName" AS "SearchBase_SearchName", "MSGFPlusSearch"."idMSGFPlusIndex" AS "MSGFPlusSearch_idMSGFPlusIndex", "MSGFPlusSearch"."idMGF" AS "MSGFPlusSearch_idMGF", "MSGFPlusSearch"."resultFilePath" AS "MSGFPlusSearch_resultFilePath", "MSGFPlusSearch"."ParentMassTolerance" AS "MSGFPlusSearch_ParentMassTolerance", "MSGFPlusSearch"."IsotopeErrorRange" AS "MSGFPlusSearch_IsotopeErrorRange", "MSGFPlusSearch"."NumOfThreads" AS "MSGFPlusSearch_NumOfThreads", "MSGFPlusSearch"."FragmentationMethodID" AS "MSGFPlusSearch_FragmentationMethodID", "MSGFPlusSearch"."InstrumentID" AS "MSGFPlusSearch_InstrumentID", "MSGFPlusSearch"."EnzymeID" AS "MSGFPlusSearch_EnzymeID", "MSGFPlusSearch"."ProtocolID" AS "MSGFPlusSearch_ProtocolID", "MSGFPlusSearch".ccm AS "MSGFPlusSearch_ccm", "MSGFPlusSearch"."idMSGFPlusModificationFile" AS "MSGFPlusSearch_idMSGFPlusModificationFile", "MSGFPlusSearch"."minPepLength" AS "MSGFPlusSearch_minPepLength", "MSGFPlusSearch"."maxPepLength" AS "MSGFPlusSearch_maxPepLength", "MSGFPlusSearch"."minPrecursorCharge" AS "MSGFPlusSearch_minPrecursorCharge", "MSGFPlusSearch"."maxPrecursorCharge" AS "MSGFPlusSearch_maxPrecursorCharge", "MSGFPlusSearch"."addFeatures" AS "MSGFPlusSearch_addFeatures" \nFROM "SearchBase" JOIN "MSGFPlusSearch" ON "SearchBase"."idSearch" = "MSGFPlusSearch"."idSearch" \nWHERE "SearchBase"."SearchName" = ?\n LIMIT ? OFFSET ?'] [parameters: ('Y3CombinedOnePercentMSGFSearch_features', 1, 0)] (Background on this error at: http://sqlalche.me/e/e3q8)
usage: RunPercolator.py [-h] [--param_file PARAM_FILE]
                        project_folder {tide,msgfplus} search_name
                        percolator_name
RunPercolator.py: error: argument search_type: invalid choice: 'msgf' (choose from 'tide', 'msgfplus')
#  ██████╗ ██╗██████╗     ██╗   ██╗ ██████╗ ██╗   ██╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗
#  ██╔══██╗██║██╔══██╗    ╚██╗ ██╔╝██╔═══██╗██║   ██║    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝
#  ██║  ██║██║██║  ██║     ╚████╔╝ ██║   ██║██║   ██║    ██║     ███████║█████╗  ██║     █████╔╝ 
#  ██║  ██║██║██║  ██║      ╚██╔╝  ██║   ██║██║   ██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ 
#  ██████╔╝██║██████╔╝       ██║   ╚██████╔╝╚██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗
#  ╚═════╝ ╚═╝╚═════╝        ╚═╝    ╚═════╝  ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
#      ████████╗██╗  ██╗███████╗                                                                 
#      ╚══██╔══╝██║  ██║██╔════╝                                                                 
#         ██║   ███████║█████╗                                                                   
#         ██║   ██╔══██║██╔══╝                                                                   
#         ██║   ██║  ██║███████╗                                                                 
#         ╚═╝   ╚═╝  ╚═╝╚══════╝                                                                 
#   ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗██╗     ██╗███████╗████████╗██████╗                   
#  ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██║     ██║██╔════╝╚══██╔══╝╚════██╗                  
#  ██║     ███████║█████╗  ██║     █████╔╝ ██║     ██║███████╗   ██║     ▄███╔╝                  
#  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██║     ██║╚════██║   ██║     ▀▀══╝                   
#  ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║███████║   ██║     ██╗                     
#   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝   ╚═╝     ╚═╝                     
#                                                                                                
project path: MurphyReplication
going to validate project integrity
current time: 20:13:52.199906
going to check fasta rows
going to check peptide list rows
going to check mgf rows
done validating project integrity
current time: 20:13:52.217141
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlite3.OperationalError: no such column: Percolator.idParameterFile

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "FilterQValue.py", line 34, in <module>
    project.filter_q_value_percolator(args.name, args.threshold, args.FilteredSearchResultName)
  File "/home/jordan/git/tidePipeline/PostProcessing.py", line 66, in filter_q_value_percolator
    percolator_handler = ReportGeneration.PercolatorHandler(percolator_name, q_value_threshold, self.project_path, self.db_session, self.get_crux_executable_path())
  File "/home/jordan/git/tidePipeline/ReportGeneration.py", line 166, in __init__
    self.percolator_row = db_session.query(DB.Percolator).filter_by(PercolatorName = name).first()
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2888, in first
    ret = list(self[0:1])
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2680, in __getitem__
    return list(res)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2988, in __iter__
    return self._execute_and_instances(context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 3011, in _execute_and_instances
    result = conn.execute(querycontext.statement, self._params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 948, in execute
    return meth(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/sql/elements.py", line 269, in _execute_on_connection
    return connection._execute_clauseelement(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1060, in _execute_clauseelement
    compiled_sql, distilled_params
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1200, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1413, in _handle_dbapi_exception
    exc_info
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 265, in raise_from_cause
    reraise(type(exception), exception, tb=exc_tb, cause=cause)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 248, in reraise
    raise value.with_traceback(tb)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: Percolator.idParameterFile [SQL: 'SELECT "Percolator"."idQValue" AS "Percolator_idQValue", "QValueBase"."idQValue" AS "QValueBase_idQValue", "QValueBase"."QValueType" AS "QValueBase_QValueType", "QValueBase"."idSearchBase" AS "QValueBase_idSearchBase", "Percolator"."idSearch" AS "Percolator_idSearch", "Percolator"."PercolatorName" AS "Percolator_PercolatorName", "Percolator"."PercolatorOutputPath" AS "Percolator_PercolatorOutputPath", "Percolator"."inputParamFilePath" AS "Percolator_inputParamFilePath", "Percolator"."idParameterFile" AS "Percolator_idParameterFile" \nFROM "QValueBase" JOIN "Percolator" ON "QValueBase"."idQValue" = "Percolator"."idQValue" \nWHERE "Percolator"."PercolatorName" = ?\n LIMIT ? OFFSET ?'] [parameters: ('Y3CombinedOnePercentMSGFSearchFilter_features_percolator', 1, 0)] (Background on this error at: http://sqlalche.me/e/e3q8)
Traceback (most recent call last):
  File "ExportPeptides.py", line 31, in <module>
    assert(args.overwrite or (not os.path.isfile(args.export_location)))
AssertionError
#  ██████╗ ██╗██████╗     ██╗   ██╗ ██████╗ ██╗   ██╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗
#  ██╔══██╗██║██╔══██╗    ╚██╗ ██╔╝██╔═══██╗██║   ██║    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝
#  ██║  ██║██║██║  ██║     ╚████╔╝ ██║   ██║██║   ██║    ██║     ███████║█████╗  ██║     █████╔╝ 
#  ██║  ██║██║██║  ██║      ╚██╔╝  ██║   ██║██║   ██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ 
#  ██████╔╝██║██████╔╝       ██║   ╚██████╔╝╚██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗
#  ╚═════╝ ╚═╝╚═════╝        ╚═╝    ╚═════╝  ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
#      ████████╗██╗  ██╗███████╗                                                                 
#      ╚══██╔══╝██║  ██║██╔════╝                                                                 
#         ██║   ███████║█████╗                                                                   
#         ██║   ██╔══██║██╔══╝                                                                   
#         ██║   ██║  ██║███████╗                                                                 
#         ╚═╝   ╚═╝  ╚═╝╚══════╝                                                                 
#   ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗██╗     ██╗███████╗████████╗██████╗                   
#  ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██║     ██║██╔════╝╚══██╔══╝╚════██╗                  
#  ██║     ███████║█████╗  ██║     █████╔╝ ██║     ██║███████╗   ██║     ▄███╔╝                  
#  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██║     ██║╚════██║   ██║     ▀▀══╝                   
#  ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║███████║   ██║     ██╗                     
#   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝   ╚═╝     ╚═╝                     
#                                                                                                
project folder: MurphyReplication
project path: MurphyReplication
going to begin command session
going to validate project integrity
current time: 20:13:53.983759
going to check fasta rows
going to check peptide list rows
going to check mgf rows
done validating project integrity
current time: 20:13:54.005905
starting command session
got MSGF+ search runner
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlite3.OperationalError: no such column: MSGFPlusSearch.addFeatures

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "RunMSGFPlusSearch.py", line 47, in <module>
    project.run_search(args.mgf_name, args.index_name, modifications_name, search_runner, args.search_name, args.memory)
  File "/home/jordan/git/tidePipeline/MSGFPlusEngine.py", line 118, in run_search
    search_row = self.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName=search_name).first()
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2888, in first
    ret = list(self[0:1])
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2680, in __getitem__
    return list(res)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2988, in __iter__
    return self._execute_and_instances(context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 3011, in _execute_and_instances
    result = conn.execute(querycontext.statement, self._params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 948, in execute
    return meth(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/sql/elements.py", line 269, in _execute_on_connection
    return connection._execute_clauseelement(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1060, in _execute_clauseelement
    compiled_sql, distilled_params
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1200, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1413, in _handle_dbapi_exception
    exc_info
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 265, in raise_from_cause
    reraise(type(exception), exception, tb=exc_tb, cause=cause)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 248, in reraise
    raise value.with_traceback(tb)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: MSGFPlusSearch.addFeatures [SQL: 'SELECT "MSGFPlusSearch"."idSearch" AS "MSGFPlusSearch_idSearch", "SearchBase"."idSearch" AS "SearchBase_idSearch", "SearchBase"."searchType" AS "SearchBase_searchType", "SearchBase"."SearchName" AS "SearchBase_SearchName", "MSGFPlusSearch"."idMSGFPlusIndex" AS "MSGFPlusSearch_idMSGFPlusIndex", "MSGFPlusSearch"."idMGF" AS "MSGFPlusSearch_idMGF", "MSGFPlusSearch"."resultFilePath" AS "MSGFPlusSearch_resultFilePath", "MSGFPlusSearch"."ParentMassTolerance" AS "MSGFPlusSearch_ParentMassTolerance", "MSGFPlusSearch"."IsotopeErrorRange" AS "MSGFPlusSearch_IsotopeErrorRange", "MSGFPlusSearch"."NumOfThreads" AS "MSGFPlusSearch_NumOfThreads", "MSGFPlusSearch"."FragmentationMethodID" AS "MSGFPlusSearch_FragmentationMethodID", "MSGFPlusSearch"."InstrumentID" AS "MSGFPlusSearch_InstrumentID", "MSGFPlusSearch"."EnzymeID" AS "MSGFPlusSearch_EnzymeID", "MSGFPlusSearch"."ProtocolID" AS "MSGFPlusSearch_ProtocolID", "MSGFPlusSearch".ccm AS "MSGFPlusSearch_ccm", "MSGFPlusSearch"."idMSGFPlusModificationFile" AS "MSGFPlusSearch_idMSGFPlusModificationFile", "MSGFPlusSearch"."minPepLength" AS "MSGFPlusSearch_minPepLength", "MSGFPlusSearch"."maxPepLength" AS "MSGFPlusSearch_maxPepLength", "MSGFPlusSearch"."minPrecursorCharge" AS "MSGFPlusSearch_minPrecursorCharge", "MSGFPlusSearch"."maxPrecursorCharge" AS "MSGFPlusSearch_maxPrecursorCharge", "MSGFPlusSearch"."addFeatures" AS "MSGFPlusSearch_addFeatures" \nFROM "SearchBase" JOIN "MSGFPlusSearch" ON "SearchBase"."idSearch" = "MSGFPlusSearch"."idSearch" \nWHERE "SearchBase"."SearchName" = ?\n LIMIT ? OFFSET ?'] [parameters: ('B22CombinedOnePercentMSGFSearch_features', 1, 0)] (Background on this error at: http://sqlalche.me/e/e3q8)
usage: RunPercolator.py [-h] [--param_file PARAM_FILE]
                        project_folder {tide,msgfplus} search_name
                        percolator_name
RunPercolator.py: error: argument search_type: invalid choice: 'msgf' (choose from 'tide', 'msgfplus')
#  ██████╗ ██╗██████╗     ██╗   ██╗ ██████╗ ██╗   ██╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗
#  ██╔══██╗██║██╔══██╗    ╚██╗ ██╔╝██╔═══██╗██║   ██║    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝
#  ██║  ██║██║██║  ██║     ╚████╔╝ ██║   ██║██║   ██║    ██║     ███████║█████╗  ██║     █████╔╝ 
#  ██║  ██║██║██║  ██║      ╚██╔╝  ██║   ██║██║   ██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ 
#  ██████╔╝██║██████╔╝       ██║   ╚██████╔╝╚██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗
#  ╚═════╝ ╚═╝╚═════╝        ╚═╝    ╚═════╝  ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
#      ████████╗██╗  ██╗███████╗                                                                 
#      ╚══██╔══╝██║  ██║██╔════╝                                                                 
#         ██║   ███████║█████╗                                                                   
#         ██║   ██╔══██║██╔══╝                                                                   
#         ██║   ██║  ██║███████╗                                                                 
#         ╚═╝   ╚═╝  ╚═╝╚══════╝                                                                 
#   ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗██╗     ██╗███████╗████████╗██████╗                   
#  ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██║     ██║██╔════╝╚══██╔══╝╚════██╗                  
#  ██║     ███████║█████╗  ██║     █████╔╝ ██║     ██║███████╗   ██║     ▄███╔╝                  
#  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██║     ██║╚════██║   ██║     ▀▀══╝                   
#  ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║███████║   ██║     ██╗                     
#   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝   ╚═╝     ╚═╝                     
#                                                                                                
project path: MurphyReplication
going to validate project integrity
current time: 20:13:55.859410
going to check fasta rows
going to check peptide list rows
going to check mgf rows
done validating project integrity
current time: 20:13:55.876897
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlite3.OperationalError: no such column: Percolator.idParameterFile

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "FilterQValue.py", line 34, in <module>
    project.filter_q_value_percolator(args.name, args.threshold, args.FilteredSearchResultName)
  File "/home/jordan/git/tidePipeline/PostProcessing.py", line 66, in filter_q_value_percolator
    percolator_handler = ReportGeneration.PercolatorHandler(percolator_name, q_value_threshold, self.project_path, self.db_session, self.get_crux_executable_path())
  File "/home/jordan/git/tidePipeline/ReportGeneration.py", line 166, in __init__
    self.percolator_row = db_session.query(DB.Percolator).filter_by(PercolatorName = name).first()
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2888, in first
    ret = list(self[0:1])
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2680, in __getitem__
    return list(res)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2988, in __iter__
    return self._execute_and_instances(context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 3011, in _execute_and_instances
    result = conn.execute(querycontext.statement, self._params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 948, in execute
    return meth(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/sql/elements.py", line 269, in _execute_on_connection
    return connection._execute_clauseelement(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1060, in _execute_clauseelement
    compiled_sql, distilled_params
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1200, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1413, in _handle_dbapi_exception
    exc_info
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 265, in raise_from_cause
    reraise(type(exception), exception, tb=exc_tb, cause=cause)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 248, in reraise
    raise value.with_traceback(tb)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: Percolator.idParameterFile [SQL: 'SELECT "Percolator"."idQValue" AS "Percolator_idQValue", "QValueBase"."idQValue" AS "QValueBase_idQValue", "QValueBase"."QValueType" AS "QValueBase_QValueType", "QValueBase"."idSearchBase" AS "QValueBase_idSearchBase", "Percolator"."idSearch" AS "Percolator_idSearch", "Percolator"."PercolatorName" AS "Percolator_PercolatorName", "Percolator"."PercolatorOutputPath" AS "Percolator_PercolatorOutputPath", "Percolator"."inputParamFilePath" AS "Percolator_inputParamFilePath", "Percolator"."idParameterFile" AS "Percolator_idParameterFile" \nFROM "QValueBase" JOIN "Percolator" ON "QValueBase"."idQValue" = "Percolator"."idQValue" \nWHERE "Percolator"."PercolatorName" = ?\n LIMIT ? OFFSET ?'] [parameters: ('B22CombinedOnePercentMSGFSearch_features_percolator', 1, 0)] (Background on this error at: http://sqlalche.me/e/e3q8)
Traceback (most recent call last):
  File "ExportPeptides.py", line 31, in <module>
    assert(args.overwrite or (not os.path.isfile(args.export_location)))
AssertionError
#  ██████╗ ██╗██████╗     ██╗   ██╗ ██████╗ ██╗   ██╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗
#  ██╔══██╗██║██╔══██╗    ╚██╗ ██╔╝██╔═══██╗██║   ██║    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝
#  ██║  ██║██║██║  ██║     ╚████╔╝ ██║   ██║██║   ██║    ██║     ███████║█████╗  ██║     █████╔╝ 
#  ██║  ██║██║██║  ██║      ╚██╔╝  ██║   ██║██║   ██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ 
#  ██████╔╝██║██████╔╝       ██║   ╚██████╔╝╚██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗
#  ╚═════╝ ╚═╝╚═════╝        ╚═╝    ╚═════╝  ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
#      ████████╗██╗  ██╗███████╗                                                                 
#      ╚══██╔══╝██║  ██║██╔════╝                                                                 
#         ██║   ███████║█████╗                                                                   
#         ██║   ██╔══██║██╔══╝                                                                   
#         ██║   ██║  ██║███████╗                                                                 
#         ╚═╝   ╚═╝  ╚═╝╚══════╝                                                                 
#   ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗██╗     ██╗███████╗████████╗██████╗                   
#  ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██║     ██║██╔════╝╚══██╔══╝╚════██╗                  
#  ██║     ███████║█████╗  ██║     █████╔╝ ██║     ██║███████╗   ██║     ▄███╔╝                  
#  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██║     ██║╚════██║   ██║     ▀▀══╝                   
#  ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║███████║   ██║     ██╗                     
#   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝   ╚═╝     ╚═╝                     
#                                                                                                
project folder: MurphyReplication
project path: MurphyReplication
going to begin command session
going to validate project integrity
current time: 20:13:57.651930
going to check fasta rows
going to check peptide list rows
going to check mgf rows
done validating project integrity
current time: 20:13:57.670183
starting command session
got MSGF+ search runner
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlite3.OperationalError: no such column: MSGFPlusSearch.addFeatures

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "RunMSGFPlusSearch.py", line 47, in <module>
    project.run_search(args.mgf_name, args.index_name, modifications_name, search_runner, args.search_name, args.memory)
  File "/home/jordan/git/tidePipeline/MSGFPlusEngine.py", line 118, in run_search
    search_row = self.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName=search_name).first()
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2888, in first
    ret = list(self[0:1])
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2680, in __getitem__
    return list(res)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2988, in __iter__
    return self._execute_and_instances(context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 3011, in _execute_and_instances
    result = conn.execute(querycontext.statement, self._params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 948, in execute
    return meth(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/sql/elements.py", line 269, in _execute_on_connection
    return connection._execute_clauseelement(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1060, in _execute_clauseelement
    compiled_sql, distilled_params
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1200, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1413, in _handle_dbapi_exception
    exc_info
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 265, in raise_from_cause
    reraise(type(exception), exception, tb=exc_tb, cause=cause)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 248, in reraise
    raise value.with_traceback(tb)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: MSGFPlusSearch.addFeatures [SQL: 'SELECT "MSGFPlusSearch"."idSearch" AS "MSGFPlusSearch_idSearch", "SearchBase"."idSearch" AS "SearchBase_idSearch", "SearchBase"."searchType" AS "SearchBase_searchType", "SearchBase"."SearchName" AS "SearchBase_SearchName", "MSGFPlusSearch"."idMSGFPlusIndex" AS "MSGFPlusSearch_idMSGFPlusIndex", "MSGFPlusSearch"."idMGF" AS "MSGFPlusSearch_idMGF", "MSGFPlusSearch"."resultFilePath" AS "MSGFPlusSearch_resultFilePath", "MSGFPlusSearch"."ParentMassTolerance" AS "MSGFPlusSearch_ParentMassTolerance", "MSGFPlusSearch"."IsotopeErrorRange" AS "MSGFPlusSearch_IsotopeErrorRange", "MSGFPlusSearch"."NumOfThreads" AS "MSGFPlusSearch_NumOfThreads", "MSGFPlusSearch"."FragmentationMethodID" AS "MSGFPlusSearch_FragmentationMethodID", "MSGFPlusSearch"."InstrumentID" AS "MSGFPlusSearch_InstrumentID", "MSGFPlusSearch"."EnzymeID" AS "MSGFPlusSearch_EnzymeID", "MSGFPlusSearch"."ProtocolID" AS "MSGFPlusSearch_ProtocolID", "MSGFPlusSearch".ccm AS "MSGFPlusSearch_ccm", "MSGFPlusSearch"."idMSGFPlusModificationFile" AS "MSGFPlusSearch_idMSGFPlusModificationFile", "MSGFPlusSearch"."minPepLength" AS "MSGFPlusSearch_minPepLength", "MSGFPlusSearch"."maxPepLength" AS "MSGFPlusSearch_maxPepLength", "MSGFPlusSearch"."minPrecursorCharge" AS "MSGFPlusSearch_minPrecursorCharge", "MSGFPlusSearch"."maxPrecursorCharge" AS "MSGFPlusSearch_maxPrecursorCharge", "MSGFPlusSearch"."addFeatures" AS "MSGFPlusSearch_addFeatures" \nFROM "SearchBase" JOIN "MSGFPlusSearch" ON "SearchBase"."idSearch" = "MSGFPlusSearch"."idSearch" \nWHERE "SearchBase"."SearchName" = ?\n LIMIT ? OFFSET ?'] [parameters: ('Y3CombinedTwoPercentMSGFSearch_features', 1, 0)] (Background on this error at: http://sqlalche.me/e/e3q8)
usage: RunPercolator.py [-h] [--param_file PARAM_FILE]
                        project_folder {tide,msgfplus} search_name
                        percolator_name
RunPercolator.py: error: argument search_type: invalid choice: 'msgf' (choose from 'tide', 'msgfplus')
#  ██████╗ ██╗██████╗     ██╗   ██╗ ██████╗ ██╗   ██╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗
#  ██╔══██╗██║██╔══██╗    ╚██╗ ██╔╝██╔═══██╗██║   ██║    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝
#  ██║  ██║██║██║  ██║     ╚████╔╝ ██║   ██║██║   ██║    ██║     ███████║█████╗  ██║     █████╔╝ 
#  ██║  ██║██║██║  ██║      ╚██╔╝  ██║   ██║██║   ██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ 
#  ██████╔╝██║██████╔╝       ██║   ╚██████╔╝╚██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗
#  ╚═════╝ ╚═╝╚═════╝        ╚═╝    ╚═════╝  ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
#      ████████╗██╗  ██╗███████╗                                                                 
#      ╚══██╔══╝██║  ██║██╔════╝                                                                 
#         ██║   ███████║█████╗                                                                   
#         ██║   ██╔══██║██╔══╝                                                                   
#         ██║   ██║  ██║███████╗                                                                 
#         ╚═╝   ╚═╝  ╚═╝╚══════╝                                                                 
#   ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗██╗     ██╗███████╗████████╗██████╗                   
#  ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██║     ██║██╔════╝╚══██╔══╝╚════██╗                  
#  ██║     ███████║█████╗  ██║     █████╔╝ ██║     ██║███████╗   ██║     ▄███╔╝                  
#  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██║     ██║╚════██║   ██║     ▀▀══╝                   
#  ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║███████║   ██║     ██╗                     
#   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝   ╚═╝     ╚═╝                     
#                                                                                                
project path: MurphyReplication
going to validate project integrity
current time: 20:13:59.511234
going to check fasta rows
going to check peptide list rows
going to check mgf rows
done validating project integrity
current time: 20:13:59.528546
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlite3.OperationalError: no such column: Percolator.idParameterFile

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "FilterQValue.py", line 34, in <module>
    project.filter_q_value_percolator(args.name, args.threshold, args.FilteredSearchResultName)
  File "/home/jordan/git/tidePipeline/PostProcessing.py", line 66, in filter_q_value_percolator
    percolator_handler = ReportGeneration.PercolatorHandler(percolator_name, q_value_threshold, self.project_path, self.db_session, self.get_crux_executable_path())
  File "/home/jordan/git/tidePipeline/ReportGeneration.py", line 166, in __init__
    self.percolator_row = db_session.query(DB.Percolator).filter_by(PercolatorName = name).first()
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2888, in first
    ret = list(self[0:1])
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2680, in __getitem__
    return list(res)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2988, in __iter__
    return self._execute_and_instances(context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 3011, in _execute_and_instances
    result = conn.execute(querycontext.statement, self._params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 948, in execute
    return meth(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/sql/elements.py", line 269, in _execute_on_connection
    return connection._execute_clauseelement(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1060, in _execute_clauseelement
    compiled_sql, distilled_params
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1200, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1413, in _handle_dbapi_exception
    exc_info
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 265, in raise_from_cause
    reraise(type(exception), exception, tb=exc_tb, cause=cause)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 248, in reraise
    raise value.with_traceback(tb)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: Percolator.idParameterFile [SQL: 'SELECT "Percolator"."idQValue" AS "Percolator_idQValue", "QValueBase"."idQValue" AS "QValueBase_idQValue", "QValueBase"."QValueType" AS "QValueBase_QValueType", "QValueBase"."idSearchBase" AS "QValueBase_idSearchBase", "Percolator"."idSearch" AS "Percolator_idSearch", "Percolator"."PercolatorName" AS "Percolator_PercolatorName", "Percolator"."PercolatorOutputPath" AS "Percolator_PercolatorOutputPath", "Percolator"."inputParamFilePath" AS "Percolator_inputParamFilePath", "Percolator"."idParameterFile" AS "Percolator_idParameterFile" \nFROM "QValueBase" JOIN "Percolator" ON "QValueBase"."idQValue" = "Percolator"."idQValue" \nWHERE "Percolator"."PercolatorName" = ?\n LIMIT ? OFFSET ?'] [parameters: ('Y3CombinedTwoPercentMSGFSearchFilter_features_percolator', 1, 0)] (Background on this error at: http://sqlalche.me/e/e3q8)
Traceback (most recent call last):
  File "ExportPeptides.py", line 31, in <module>
    assert(args.overwrite or (not os.path.isfile(args.export_location)))
AssertionError
#  ██████╗ ██╗██████╗     ██╗   ██╗ ██████╗ ██╗   ██╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗
#  ██╔══██╗██║██╔══██╗    ╚██╗ ██╔╝██╔═══██╗██║   ██║    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝
#  ██║  ██║██║██║  ██║     ╚████╔╝ ██║   ██║██║   ██║    ██║     ███████║█████╗  ██║     █████╔╝ 
#  ██║  ██║██║██║  ██║      ╚██╔╝  ██║   ██║██║   ██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ 
#  ██████╔╝██║██████╔╝       ██║   ╚██████╔╝╚██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗
#  ╚═════╝ ╚═╝╚═════╝        ╚═╝    ╚═════╝  ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
#      ████████╗██╗  ██╗███████╗                                                                 
#      ╚══██╔══╝██║  ██║██╔════╝                                                                 
#         ██║   ███████║█████╗                                                                   
#         ██║   ██╔══██║██╔══╝                                                                   
#         ██║   ██║  ██║███████╗                                                                 
#         ╚═╝   ╚═╝  ╚═╝╚══════╝                                                                 
#   ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗██╗     ██╗███████╗████████╗██████╗                   
#  ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██║     ██║██╔════╝╚══██╔══╝╚════██╗                  
#  ██║     ███████║█████╗  ██║     █████╔╝ ██║     ██║███████╗   ██║     ▄███╔╝                  
#  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██║     ██║╚════██║   ██║     ▀▀══╝                   
#  ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║███████║   ██║     ██╗                     
#   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝   ╚═╝     ╚═╝                     
#                                                                                                
project folder: MurphyReplication
project path: MurphyReplication
going to begin command session
going to validate project integrity
current time: 20:14:01.311627
going to check fasta rows
going to check peptide list rows
going to check mgf rows
done validating project integrity
current time: 20:14:01.333773
starting command session
got MSGF+ search runner
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlite3.OperationalError: no such column: MSGFPlusSearch.addFeatures

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "RunMSGFPlusSearch.py", line 47, in <module>
    project.run_search(args.mgf_name, args.index_name, modifications_name, search_runner, args.search_name, args.memory)
  File "/home/jordan/git/tidePipeline/MSGFPlusEngine.py", line 118, in run_search
    search_row = self.db_session.query(DB.MSGFPlusSearch).filter_by(SearchName=search_name).first()
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2888, in first
    ret = list(self[0:1])
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2680, in __getitem__
    return list(res)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2988, in __iter__
    return self._execute_and_instances(context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 3011, in _execute_and_instances
    result = conn.execute(querycontext.statement, self._params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 948, in execute
    return meth(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/sql/elements.py", line 269, in _execute_on_connection
    return connection._execute_clauseelement(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1060, in _execute_clauseelement
    compiled_sql, distilled_params
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1200, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1413, in _handle_dbapi_exception
    exc_info
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 265, in raise_from_cause
    reraise(type(exception), exception, tb=exc_tb, cause=cause)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 248, in reraise
    raise value.with_traceback(tb)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: MSGFPlusSearch.addFeatures [SQL: 'SELECT "MSGFPlusSearch"."idSearch" AS "MSGFPlusSearch_idSearch", "SearchBase"."idSearch" AS "SearchBase_idSearch", "SearchBase"."searchType" AS "SearchBase_searchType", "SearchBase"."SearchName" AS "SearchBase_SearchName", "MSGFPlusSearch"."idMSGFPlusIndex" AS "MSGFPlusSearch_idMSGFPlusIndex", "MSGFPlusSearch"."idMGF" AS "MSGFPlusSearch_idMGF", "MSGFPlusSearch"."resultFilePath" AS "MSGFPlusSearch_resultFilePath", "MSGFPlusSearch"."ParentMassTolerance" AS "MSGFPlusSearch_ParentMassTolerance", "MSGFPlusSearch"."IsotopeErrorRange" AS "MSGFPlusSearch_IsotopeErrorRange", "MSGFPlusSearch"."NumOfThreads" AS "MSGFPlusSearch_NumOfThreads", "MSGFPlusSearch"."FragmentationMethodID" AS "MSGFPlusSearch_FragmentationMethodID", "MSGFPlusSearch"."InstrumentID" AS "MSGFPlusSearch_InstrumentID", "MSGFPlusSearch"."EnzymeID" AS "MSGFPlusSearch_EnzymeID", "MSGFPlusSearch"."ProtocolID" AS "MSGFPlusSearch_ProtocolID", "MSGFPlusSearch".ccm AS "MSGFPlusSearch_ccm", "MSGFPlusSearch"."idMSGFPlusModificationFile" AS "MSGFPlusSearch_idMSGFPlusModificationFile", "MSGFPlusSearch"."minPepLength" AS "MSGFPlusSearch_minPepLength", "MSGFPlusSearch"."maxPepLength" AS "MSGFPlusSearch_maxPepLength", "MSGFPlusSearch"."minPrecursorCharge" AS "MSGFPlusSearch_minPrecursorCharge", "MSGFPlusSearch"."maxPrecursorCharge" AS "MSGFPlusSearch_maxPrecursorCharge", "MSGFPlusSearch"."addFeatures" AS "MSGFPlusSearch_addFeatures" \nFROM "SearchBase" JOIN "MSGFPlusSearch" ON "SearchBase"."idSearch" = "MSGFPlusSearch"."idSearch" \nWHERE "SearchBase"."SearchName" = ?\n LIMIT ? OFFSET ?'] [parameters: ('B22CombinedOnePercentMSGFSearch_features', 1, 0)] (Background on this error at: http://sqlalche.me/e/e3q8)
usage: RunPercolator.py [-h] [--param_file PARAM_FILE]
                        project_folder {tide,msgfplus} search_name
                        percolator_name
RunPercolator.py: error: argument search_type: invalid choice: 'msgf' (choose from 'tide', 'msgfplus')
#  ██████╗ ██╗██████╗     ██╗   ██╗ ██████╗ ██╗   ██╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗
#  ██╔══██╗██║██╔══██╗    ╚██╗ ██╔╝██╔═══██╗██║   ██║    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝
#  ██║  ██║██║██║  ██║     ╚████╔╝ ██║   ██║██║   ██║    ██║     ███████║█████╗  ██║     █████╔╝ 
#  ██║  ██║██║██║  ██║      ╚██╔╝  ██║   ██║██║   ██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ 
#  ██████╔╝██║██████╔╝       ██║   ╚██████╔╝╚██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗
#  ╚═════╝ ╚═╝╚═════╝        ╚═╝    ╚═════╝  ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
#      ████████╗██╗  ██╗███████╗                                                                 
#      ╚══██╔══╝██║  ██║██╔════╝                                                                 
#         ██║   ███████║█████╗                                                                   
#         ██║   ██╔══██║██╔══╝                                                                   
#         ██║   ██║  ██║███████╗                                                                 
#         ╚═╝   ╚═╝  ╚═╝╚══════╝                                                                 
#   ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗██╗     ██╗███████╗████████╗██████╗                   
#  ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██║     ██║██╔════╝╚══██╔══╝╚════██╗                  
#  ██║     ███████║█████╗  ██║     █████╔╝ ██║     ██║███████╗   ██║     ▄███╔╝                  
#  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██║     ██║╚════██║   ██║     ▀▀══╝                   
#  ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║███████║   ██║     ██╗                     
#   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝   ╚═╝     ╚═╝                     
#                                                                                                
project path: MurphyReplication
going to validate project integrity
current time: 20:14:03.229634
going to check fasta rows
going to check peptide list rows
going to check mgf rows
done validating project integrity
current time: 20:14:03.248037
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlite3.OperationalError: no such column: Percolator.idParameterFile

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "FilterQValue.py", line 34, in <module>
    project.filter_q_value_percolator(args.name, args.threshold, args.FilteredSearchResultName)
  File "/home/jordan/git/tidePipeline/PostProcessing.py", line 66, in filter_q_value_percolator
    percolator_handler = ReportGeneration.PercolatorHandler(percolator_name, q_value_threshold, self.project_path, self.db_session, self.get_crux_executable_path())
  File "/home/jordan/git/tidePipeline/ReportGeneration.py", line 166, in __init__
    self.percolator_row = db_session.query(DB.Percolator).filter_by(PercolatorName = name).first()
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2888, in first
    ret = list(self[0:1])
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2680, in __getitem__
    return list(res)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 2988, in __iter__
    return self._execute_and_instances(context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/orm/query.py", line 3011, in _execute_and_instances
    result = conn.execute(querycontext.statement, self._params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 948, in execute
    return meth(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/sql/elements.py", line 269, in _execute_on_connection
    return connection._execute_clauseelement(self, multiparams, params)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1060, in _execute_clauseelement
    compiled_sql, distilled_params
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1200, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1413, in _handle_dbapi_exception
    exc_info
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 265, in raise_from_cause
    reraise(type(exception), exception, tb=exc_tb, cause=cause)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/util/compat.py", line 248, in reraise
    raise value.with_traceback(tb)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/base.py", line 1193, in _execute_context
    context)
  File "/usr/local/lib/python3.5/dist-packages/sqlalchemy/engine/default.py", line 509, in do_execute
    cursor.execute(statement, parameters)
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: Percolator.idParameterFile [SQL: 'SELECT "Percolator"."idQValue" AS "Percolator_idQValue", "QValueBase"."idQValue" AS "QValueBase_idQValue", "QValueBase"."QValueType" AS "QValueBase_QValueType", "QValueBase"."idSearchBase" AS "QValueBase_idSearchBase", "Percolator"."idSearch" AS "Percolator_idSearch", "Percolator"."PercolatorName" AS "Percolator_PercolatorName", "Percolator"."PercolatorOutputPath" AS "Percolator_PercolatorOutputPath", "Percolator"."inputParamFilePath" AS "Percolator_inputParamFilePath", "Percolator"."idParameterFile" AS "Percolator_idParameterFile" \nFROM "QValueBase" JOIN "Percolator" ON "QValueBase"."idQValue" = "Percolator"."idQValue" \nWHERE "Percolator"."PercolatorName" = ?\n LIMIT ? OFFSET ?'] [parameters: ('B22CombinedTwoPercentMSGFSearch_features_percolator', 1, 0)] (Background on this error at: http://sqlalche.me/e/e3q8)
Traceback (most recent call last):
  File "ExportPeptides.py", line 31, in <module>
    assert(args.overwrite or (not os.path.isfile(args.export_location)))
AssertionError
