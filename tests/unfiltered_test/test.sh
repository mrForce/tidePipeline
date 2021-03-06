#!/bin/bash

cd ..
cd ..
ls
python3 AddRAW.py UnfilteredTest ~/Downloads/160127_609_015_EL4_B22.raw B22RAW
python3 RunMaxQuantSearch.py UnfilteredTest B22RAW FirstMaxQuantConfig 0.01 TargetSet CombinedMousePeptides CombinedMouseMaxQuantSearch_B22
python3 ExportPeptides.py UnfilteredTest MaxQuantSearch CombinedMouseMaxQuantSearch_B22 tests/unfiltered_test/maxquant_b22.txt
python3 AddMGF.py UnfilteredTest ~/Downloads/160127_609_015_EL4_B22.mgf B22_mgf
#note: the Y3 is inconsequential in the index name, since this is unfiltered.
python3 RunTideSearch.py UnfilteredTest B22_mgf CombinedMouseY3_index_custom_enzymes CombinedMouseB22_tide_search --num-threads 1 --top-match 1
python3 RunAssignConfidence.py UnfilteredTest CombinedMouseB22_tide_search B22Mouse_assign_confidence
python3 RunPercolator.py UnfilteredTest CombinedMouseB22_tide_search B22MousePercolator --param_file tests/unfiltered_test/percolator_param_file.params
python3 FilterQValue.py UnfilteredTest assign_confidence B22Mouse_assign_confidence 0.01 B22_mouse_assign_one_percent_fdr 
python3 FilterQValue.py UnfilteredTest percolator B22MousePercolator 0.01 B22_mouse_percolator_one_percent_fdr
python3 ExportPeptides.py UnfilteredTest FilteredSearchResult B22_mouse_assign_one_percent_fdr tests/unfiltered_test/assignconfidence_b22.txt
python3 ExportPeptides.py UnfilteredTest FilteredSearchResult B22_mouse_percolator_one_percent_fdr tests/unfiltered_test/percolator_b22.txt
python3 RunMSGFPlusSearch.py UnfilteredTest B22_mgf MousePeptideIndex B22MouseMSGFSearch --thread 4 --memory 30000
python3 FilterQValue.py UnfilteredTest MSGF B22MouseMSGFSearch 0.01 B22MouseMSGF_one_percent_fdr
python3 ExportPeptides.py UnfilteredTest FilteredSearchResult B22MouseMSGF_one_percent_fdr tests/unfiltered_test/msgf_b22.txt
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
#echo "about to do MaxQuant search"#
#python3 RunMaxQuantSearch.py UnfilteredTest Y3RAW FirstMaxQuantConfig 0.01 TargetSet CombinedMousePeptides CombinedMouseMaxQuantSearch_one_percent_fdr
#zip -r MaxQuantTest.zip MaxQuantTest
#python3 CreateMSGFPlusIndex.py UnfilteredTest TargetSet CombinedMousePeptides MousePeptideIndex --memory 6000
#python3 AddMGF.py UnfilteredTest ~/Downloads/160127_609_015_EL4_Y3.mgf Y3_mgf
#zip -r Y3_test_project.zip Y3_test_project
#python3 RunMSGFPlusSearch.py UnfilteredTest Y3_mgf MousePeptideIndex MouseMSGFSearch_no_enzyme_four --thread 4 --memory 30000
#python KChop.py Y3_test_project MouseProteins 10 MouseProteinTenMers
#python RunNetMHC.py Y3_test_project MouseProteinNineMers H-2-Kb 2 MouseProteinNineMersH2Kb
#python RunNetMHC.py Y3_test_project MouseProteinTenMers H-2-Kb 2 MouseProteinTenMersH2Kb
#python CreateTargetSet.py Y3_test_project --FilteredNetMHC MouseProteinNineMersH2Kb --FilteredNetMHC MouseProteinTenMersH2Kb H2KbPeptideSet
#python3 CreateTideIndex.py UnfilteredTest TargetSet CombinedMousePeptides CombinedMouseY3_index_custom_enzymes --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme
#python AddMGF.py Y3_test_project  tests/Y3Test/160127_609_015_EL4_Y3.mgf Y3_mgf
#python3 RunTideSearch.py UnfilteredTest Y3_mgf CombinedMouseY3_index_custom_enzymes CombinedMouseY3_search_custom_enzyme_top_match_one_single_threads --num-threads 1 --top-match 1

#python3 RunAssignConfidence.py UnfilteredTest CombinedMouseY3_search_custom_enzyme_top_match_one_single_threads Y3MouseTideSearchConfidence_custom_enzyme_three_single_thread
#python3 RunPercolator.py UnfilteredTest CombinedMouseY3_search_custom_enzyme_top_match_one_single_threads Y3Percolator_custom_enzyme_six_single_thread --param_file tests/unfiltered_test/percolator_param_file.params
#python3 FilterQValue.py UnfilteredTest assign_confidence Y3MouseTideSearchConfidence_custom_enzyme_three_single_thread 0.01 Y3MouseTideFiltered_custom_enzyme_three_single_thread
#python3 FilterQValue.py UnfilteredTest percolator Y3Percolator_custom_enzyme_six_single_thread 0.01 Y3PercolatorFiltered_custom_enzyme_six_single_thread
#python3 FilterQValue.py UnfilteredTest MSGF MouseMSGFSearch_no_enzyme_four 0.01 Y3MSGFfiltered_no_enzyme_four
#python3 ExportPeptides.py UnfilteredTest FilteredSearchResult Y3MSGFfiltered_no_enzyme_four tests/unfiltered_test/msgf.txt
#python3 ExportPeptides.py UnfilteredTest FilteredSearchResult Y3MouseTideFiltered_custom_enzyme_three_single_thread tests/unfiltered_test/assignconfidence.txt
#python3 ExportPeptides.py UnfilteredTest FilteredSearchResult Y3PercolatorFiltered_custom_enzyme_six_single_thread tests/unfiltered_test/percolator.txt 
#python3 ExportPeptides.py UnfilteredTest MaxQuantSearch CombinedMouseMaxQuantSearch_one_percent_fdr tests/unfiltered_test/maxquant.txt
