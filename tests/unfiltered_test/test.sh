#!/bin/bash

cd ..
cd ..
ls
#python3 Initialize.py UnfilteredTest tests/unfiltered_test/config.ini
#python3 AddMaxQuantParamFile.py UnfilteredTest tests/unfiltered_test/mqpar.xml FirstMaxQuantConfig
#python3 AddRAW.py UnfilteredTest ~/Downloads/160127_609_015_EL4_Y3.raw Y3RAW
#python AddHLA.py MaxQuantTest H-2-Kb
#python3 AddFASTA.py UnfilteredTest ~/Downloads/all_mouse_proteins.fasta MouseProteins
#python3 KChop.py UnfilteredTest MouseProteins 9 MouseProteinNineMers
#python3 KChop.py UnfilteredTest MouseProteins 8 MouseProteinEightMers
#python3 KChop.py UnfilteredTest MouseProteins 10 MouseProteinTenMers
#python3 KChop.py UnfilteredTest MouseProteins 11 MouseProteinElevenMers
#python3 CreateTargetSet.py UnfilteredTest --PeptideList MouseProteinNineMers --PeptideList MouseProteinEightMers --PeptideList MouseProteinTenMers --PeptideList MouseProteinElevenMers CombinedMousePeptides
#python KChop.py MaxQuantTest MouseProteins 12 MouseProteinTwelveMers
#python RunNetMHC.py MaxQuantTest MouseProteinEightMers H-2-Kb 2 MouseProteinEightMersH2Kb
#python RunNetMHC.py MaxQuantTest MouseProteinNineMers H-2-Kb 2 MouseProteinNineMersH2Kb
#python RunNetMHC.py MaxQuantTest MouseProteinTenMers H-2-Kb 2 MouseProteinTenMersH2Kb
#python RunNetMHC.py MaxQuantTest MouseProteinElevenMers H-2-Kb 2 MouseProteinElevenMersH2Kb
#python RunNetMHC.py MaxQuantTest MouseProteinTwelveMers H-2-Kb 2 MouseProteinTwelveMersH2Kb
#python CreateTargetSet.py MaxQuantTest --FilteredNetMHC MouseProteinEightMersH2Kb --FilteredNetMHC MouseProteinNineMersH2Kb --FilteredNetMHC MouseProteinTenMersH2Kb --FilteredNetMHC MouseProteinElevenMersH2Kb --FilteredNetMHC MouseProteinTwelveMersH2Kb CombinedMousePeptides
#echo "about to do MaxQuant search"
#python3 RunMaxQuantSearch.py UnfilteredTest Y3RAW FirstMaxQuantConfig 0.01 TargetSet CombinedMousePeptides CombinedMouseMaxQuantSearch_one_percent_fdr
#zip -r MaxQuantTest.zip MaxQuantTest
#python3 CreateMSGFPlusIndex.py UnfilteredTest TargetSet CombinedMousePeptides MousePeptideIndex --memory 6000
#python3 AddMGF.py UnfilteredTest ~/Downloads/160127_609_015_EL4_Y3.mgf Y3_mgf
#zip -r Y3_test_project.zip Y3_test_project
#python3 RunMSGFPlusSearch.py UnfilteredTest Y3_mgf MousePeptideIndex MouseMSGFSearch --memory 6000
#python KChop.py Y3_test_project MouseProteins 10 MouseProteinTenMers
#python RunNetMHC.py Y3_test_project MouseProteinNineMers H-2-Kb 2 MouseProteinNineMersH2Kb
#python RunNetMHC.py Y3_test_project MouseProteinTenMers H-2-Kb 2 MouseProteinTenMersH2Kb
#python CreateTargetSet.py Y3_test_project --FilteredNetMHC MouseProteinNineMersH2Kb --FilteredNetMHC MouseProteinTenMersH2Kb H2KbPeptideSet
#python3 CreateTideIndex.py UnfilteredTest TargetSet CombinedMousePeptides CombinedMouseY3_index
#python AddMGF.py Y3_test_project  tests/Y3Test/160127_609_015_EL4_Y3.mgf Y3_mgf
#python3 RunTideSearch.py UnfilteredTest Y3_mgf CombinedMouseY3_index CombinedMouseY3_search --num-threads=4

#python3 RunAssignConfidence.py UnfilteredTest CombinedMouseY3_search Y3MouseTideSearchConfidence
#python3 RunPercolator.py UnfilteredTest CombinedMouseY3_search Y3Percolator
#python3 FilterQValue.py UnfilteredTest assign_confidence Y3MouseTideSearchConfidence 0.01 Y3MouseTideFiltered
python3 FilterQValue.py UnfilteredTest percolator Y3Percolator 0.01 Y3PercolatorFiltered
#python ExportPeptides.py Y3_test_project FilteredSearchResult H2KbTideSearchConfidenceFiltered tests/Y3Test/assignconfidence.txt
#python ExportPeptides.py Y3_test_project FilteredSearchResult H2KbPercolatorFiltered tests/Y3Test/percolator.txt
