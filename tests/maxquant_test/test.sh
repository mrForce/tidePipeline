#!/bin/bash

cd ..
cd ..
ls
python Initialize.py MaxQuantTest tests/maxquant_test/config.ini
python AddMaxQuantParamFile.py MaxQuantTest tests/maxquant_test/mqpar.xml FirstMaxQuantConfig
python AddRAW.py MaxQuantTest ~/Downloads/160127_609_015_EL4_Y3.raw Y3RAW
python AddHLA.py MaxQuantTest H-2-Kb
python AddFASTA.py MaxQuantTest tests/Y3Test/all_mouse_proteins.fasta MouseProteins
python KChop.py MaxQuantTest MouseProteins 9 MouseProteinNineMers
echo "about to do MaxQuant search"
python RunMaxQuantSearch.py MaxQuantTest Y3RAW FirstMaxQuantConfig 0.05 PeptideList MouseProteinNineMers NineMerMaxQuantSearch

#python CreateMSGFPlusIndex.py Y3_test_project PeptideList MouseProteinNineMers MouseProteinNineMersIndex --memory 6000
#python AddMGF.py Y3_test_project  tests/Y3Test/160127_609_015_EL4_Y3.mgf Y3_mgf
#zip -r Y3_test_project.zip Y3_test_project
#python RunMSGFPlusSearch.py Y3_test_project Y3_mgf MouseProteinNineMersIndex MouseMSGFSearch --memory 6000
#python KChop.py Y3_test_project MouseProteins 10 MouseProteinTenMers
#python RunNetMHC.py Y3_test_project MouseProteinNineMers H-2-Kb 2 MouseProteinNineMersH2Kb
#python RunNetMHC.py Y3_test_project MouseProteinTenMers H-2-Kb 2 MouseProteinTenMersH2Kb
#python CreateTargetSet.py Y3_test_project --FilteredNetMHC MouseProteinNineMersH2Kb --FilteredNetMHC MouseProteinTenMersH2Kb H2KbPeptideSet
#python CreateTideIndex.py Y3_test_project TargetSet H2KbPeptideSet H2KbTideIndex
#python AddMGF.py Y3_test_project  tests/Y3Test/160127_609_015_EL4_Y3.mgf Y3_mgf
#python RunTideSearch.py Y3_test_project Y3_mgf H2KbTideIndex H2KbTideSearch
#python RunAssignConfidence.py Y3_test_project H2KbTideSearch H2KbTideSearchConfidence
#python RunPercolator.py Y3_test_project H2KbTideSearch H2KbPercolator
#python FilterQValue.py Y3_test_project assign_confidence H2KbTideSearchConfidence 0.05 H2KbTideSearchConfidenceFiltered
#python FilterQValue.py Y3_test_project percolator H2KbPercolator 0.05 H2KbPercolatorFiltered
#python ExportPeptides.py Y3_test_project FilteredSearchResult H2KbTideSearchConfidenceFiltered tests/Y3Test/assignconfidence.txt
#python ExportPeptides.py Y3_test_project FilteredSearchResult H2KbPercolatorFiltered tests/Y3Test/percolator.txt
