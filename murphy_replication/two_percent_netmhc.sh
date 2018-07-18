#!/bin/bash
cd ..
python3 RunNetMHC.py MurphyReplication MouseProteinEightMers H-2-Kb 2 MouseProteinEightMersKbTwoPercent
python3 RunNetMHC.py MurphyReplication MouseProteinNineMers H-2-Kb 2 MouseProteinNineMersKbTwoPercent
python3 RunNetMHC.py MurphyReplication MouseProteinTenMers H-2-Kb 2 MouseProteinTenMersKbTwoPercent
python3 RunNetMHC.py MurphyReplication MouseProteinElevenMers H-2-Kb 2 MouseProteinElevenMersKbTwoPercent
python3 RunNetMHC.py MurphyReplication MouseProteinEightMers H-2-Db 2 MouseProteinEightMersDbTwoPercent
python3 RunNetMHC.py MurphyReplication MouseProteinNineMers H-2-Db 2 MouseProteinNineMersDbTwoPercent
python3 RunNetMHC.py MurphyReplication MouseProteinTenMers H-2-Db 2 MouseProteinTenMersDbTwoPercent
python3 RunNetMHC.py MurphyReplication MouseProteinElevenMers H-2-Db 2 MouseProteinElevenMersDbTwoPercent

python3 CreateTargetSet.py MurphyReplication --FilteredNetMHC MouseProteinEightMersKbTwoPercent --FilteredNetMHC MouseProteinNineMersKbTwoPercent --FilteredNetMHC MouseProteinTenMersKbTwoPercent --FilteredNetMHC MouseProteinElevenMersKbTwoPercent --FilteredNetMHC MouseProteinEightMersDbTwoPercent --FilteredNetMHC MouseProteinNineMersDbTwoPercent --FilteredNetMHC MouseProteinTenMersDbTwoPercent --FilteredNetMHC MouseProteinElevenMersDbTwoPercent  CombinedTwoPercent



python3 RunMaxQuantSearch.py MurphyReplication Y3RAW MaxQuantConfig 0.01 TargetSet CombinedTwoPercent TwoPercentMaxQuantY3
python ExportPeptides.py MurphyReplication MaxQuantsearch TwoPercentMaxQuantY3 murphy_replication/maxquant_y3_twopercent.txt
python3 CreateMSGFPlusIndex.py MurphyReplication TargetSet CombinedTwoPercent CombinedTwoPercentIndex --memory 30000
python3 RunMSGFPlusSearch.py MurphyReplication Y3MGF CombinedTwoPercentIndex Y3CombinedTwoPercentMSGFSearch --thread 5 --memory 30000
python3 FilterQValue.py MurphyReplication MSGF Y3CombinedTwoPercentMSGFSearch 0.01 Y3CombinedTwoPercentMSGFSearchFilter
python3 ExportPeptides.py MurphyReplication FilteredSearchResult Y3CombinedTwoPercentMSGFSearchFilter murphy_replication/msgf_y3_twopercent.txt
python3 CreateTideIndex.py MurphyReplication TargetSet CombinedTwoPercent CombinedTwoPercentTideIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme
python3 RunTideSearch.py MurphyReplication Y3MGF CombinedTwoPercentTideIndex CombinedTwoPercentY3TideSearch --num-threads 1 --top-match 1
python3 RunPercolator.py MurphyReplication CombinedTwoPercentY3TideSearch CombinedTwoPercentY3Percolator --param_file murphy_replication/percolator.params
python3 FilterQValue.py MurphyReplication percolator CombinedTwoPercentY3Percolator 0.01 CombinedTwoPercentY3PercolatorFiltered
python3 ExportPeptides.py MurphyReplication FilteredSearchResult CombinedTwoPercentY3PercolatorFiltered murphy_replication/percolator_y3_twopercent.txt
python3 RunAssignConfidence.py MurphyReplication CombinedTwoPercentY3TideSearch CombinedTwoPercentY3TideSearchConfidence
python3 FilterQValue.py MurphyReplication assign_confidence CombinedTwoPercentY3TideSearchConfidence 0.01 CombinedTwoPercentY3TideSearchConfidenceFiltered
python3 ExportPeptides.py MurphyReplication FilteredSearchResult CombinedTwoPercentY3TideSearchConfidenceFiltered murphy_replication/assign_confidence_y3_twopercent.txt
