#!/bin/bash

cd ..
cd ..
ls
#python Initialize.py MaxQuantTest tests/maxquant_test/config.ini
#python AddMaxQuantParamFile.py MaxQuantTest tests/maxquant_test/mqpar.xml FirstMaxQuantConfig
#python AddRAW.py MaxQuantTest ~/Downloads/160127_609_015_EL4_Y3.raw Y3RAW
#python AddHLA.py MaxQuantTest H-2-Kb
#python AddFASTA.py MaxQuantTest tests/Y3Test/all_mouse_proteins.fasta MouseProteins
#python KChop.py MaxQuantTest MouseProteins 9 MouseProteinNineMers
#python KChop.py MaxQuantTest MouseProteins 8 MouseProteinEightMers
#python KChop.py MaxQuantTest MouseProteins 10 MouseProteinTenMers
#python KChop.py MaxQuantTest MouseProteins 11 MouseProteinElevenMers
#python KChop.py MaxQuantTest MouseProteins 12 MouseProteinTwelveMers
#python RunNetMHC.py MaxQuantTest MouseProteinEightMers H-2-Kb 2 MouseProteinEightMersH2Kb
#python RunNetMHC.py MaxQuantTest MouseProteinNineMers H-2-Kb 2 MouseProteinNineMersH2Kb
#python RunNetMHC.py MaxQuantTest MouseProteinTenMers H-2-Kb 2 MouseProteinTenMersH2Kb
#python RunNetMHC.py MaxQuantTest MouseProteinElevenMers H-2-Kb 2 MouseProteinElevenMersH2Kb
#python RunNetMHC.py MaxQuantTest MouseProteinTwelveMers H-2-Kb 2 MouseProteinTwelveMersH2Kb
#python CreateTargetSet.py MaxQuantTest --FilteredNetMHC MouseProteinEightMersH2Kb --FilteredNetMHC MouseProteinNineMersH2Kb --FilteredNetMHC MouseProteinTenMersH2Kb --FilteredNetMHC MouseProteinElevenMersH2Kb --FilteredNetMHC MouseProteinTwelveMersH2Kb CombinedMousePeptides
#echo "about to do MaxQuant search"
python RunMaxQuantSearch.py MaxQuantTest Y3RAW FirstMaxQuantConfig 0.05 TargetSet CombinedMousePeptides CombinedMouseMaxQuantSearchThree
#zip -r MaxQuantTest.zip MaxQuantTest
#python CreateMSGFPlusIndex.py MaxQuantTest TargetSet CombinedMousePeptides MousePeptideIndex --memory 6000
#python AddMGF.py MaxQuantTest  tests/Y3Test/160127_609_015_EL4_Y3.mgf Y3_mgf
#zip -r Y3_test_project.zip Y3_test_project
#python RunMSGFPlusSearch.py MaxQuantTest Y3_mgf MousePeptideIndex MouseMSGFSearch --memory 6000
#python KChop.py Y3_test_project MouseProteins 10 MouseProteinTenMers
#python RunNetMHC.py Y3_test_project MouseProteinNineMers H-2-Kb 2 MouseProteinNineMersH2Kb
#python RunNetMHC.py Y3_test_project MouseProteinTenMers H-2-Kb 2 MouseProteinTenMersH2Kb
#python CreateTargetSet.py Y3_test_project --FilteredNetMHC MouseProteinNineMersH2Kb --FilteredNetMHC MouseProteinTenMersH2Kb H2KbPeptideSet
#python CreateTideIndex.py MaxQuantTest TargetSet CombinedMousePeptides CombinedMouseY3_index
#python AddMGF.py Y3_test_project  tests/Y3Test/160127_609_015_EL4_Y3.mgf Y3_mgf
#python RunTideSearch.py MaxQuantTest Y3_mgf CombinedMouseY3_index CombinedMouseY3_search

python RunAssignConfidence.py MaxQuantTest CombinedMouseY3_search Y3MouseTideSearchConfidence
#python RunPercolator.py Y3_test_project H2KbTideSearch H2KbPercolator
python FilterQValue.py MaxQuantTest assign_confidence Y3MouseTideSearchConfidence 0.05 Y3MouseTideFiltered
#python FilterQValue.py Y3_test_project percolator H2KbPercolator 0.05 H2KbPercolatorFiltered
#python ExportPeptides.py Y3_test_project FilteredSearchResult H2KbTideSearchConfidenceFiltered tests/Y3Test/assignconfidence.txt
#python ExportPeptides.py Y3_test_project FilteredSearchResult H2KbPercolatorFiltered tests/Y3Test/percolator.txt
