cd ../..
python Initialize.py ContaminantTest config.ini ~/unimod.xml
python AddParamFile.py ContaminantTest tide-search tide_search.params default_search_params
python AddParamFile.py ContaminantTest percolator percolator.params default_percolator_params
python AddMGF.py ContaminantTest tests/Y3Test/160127_609_015_EL4_Y3.mgf Y3MGF
python AddHLA.py ContaminantTest H-2-Kb
python AddHLA.py ContaminantTest H-2-Db
python AddFASTA.py ContaminantTest ~/Downloads/all_mouse_proteins_head.fasta MouseProteins
python KChop.py ContaminantTest MouseProteins 9 MouseProteinNineMers
python KChop.py ContaminantTest MouseProteins 8 MouseProteinEightMers
python KChop.py ContaminantTest MouseProteins 10 MouseProteinTenMers
python KChop.py ContaminantTest MouseProteins 11 MouseProteinElevenMers
python RunNetMHC.py ContaminantTest MouseProteinEightMers H-2-Kb 2 MouseProteinsEightMersKbTwoPercent 
python RunNetMHC.py ContaminantTest MouseProteinEightMers H-2-Kb 1 MouseProteinsEightMersKbOnePercent
python RunNetMHC.py ContaminantTest MouseProteinNineMers H-2-Kb 2 MouseProteinsNineMersKbTwoPercent
python RunNetMHC.py ContaminantTest MouseProteinNineMers H-2-Kb 1 MouseProteinsNineMersKbOnePercent
python RunNetMHC.py ContaminantTest MouseProteinTenMers H-2-Kb 2 MouseProteinsTenMersKbTwoPercent
python RunNetMHC.py ContaminantTest MouseProteinTenMers H-2-Kb 1 MouseProteinsTenMersKbOnePercent
python RunNetMHC.py ContaminantTest MouseProteinElevenMers H-2-Kb 2 MouseProteinsElevenMersKbTwoPercent
python RunNetMHC.py ContaminantTest MouseProteinElevenMers H-2-Kb 1 MouseProteinsElevenMersKbOnePercent

python RunNetMHC.py ContaminantTest MouseProteinEightMers H-2-Db 2 MouseProteinsEightMersDbTwoPercent
python RunNetMHC.py ContaminantTest MouseProteinEightMers H-2-Db 1 MouseProteinsEightMersDbOnePercent
python RunNetMHC.py ContaminantTest MouseProteinNineMers H-2-Db 2 MouseProteinsNineMersDbTwoPercent
python RunNetMHC.py ContaminantTest MouseProteinNineMers H-2-Db 1 MouseProteinsNineMersDbOnePercent
python RunNetMHC.py ContaminantTest MouseProteinTenMers H-2-Db 2 MouseProteinsTenMersDbTwoPercent
python RunNetMHC.py ContaminantTest MouseProteinTenMers H-2-Db 1 MouseProteinsTenMersDbOnePercent
python RunNetMHC.py ContaminantTest MouseProteinElevenMers H-2-Db 2 MouseProteinsElevenMersDbTwoPercent
python RunNetMHC.py ContaminantTest MouseProteinElevenMers H-2-Db 1 MouseProteinsElevenMersDbOnePercent

python CreatTargetSet ContaminantTest CombinedTwoPercent --FilteredNetMHC MouseProteinsEightMersKbTwoPercent --FilteredNetMHC MouseProteinsNineMersKbTwoPercent --FilteredNetMHC MouseProteinsTenMersKbTwoPercent --FilteredNetMHC MouseProteinsElevenMersKbTwoPercent --FilteredNetMHC MouseProteinsEightMersDbTwoPercent --FilteredNetMHC MouseProteinsNineMersDbTwoPercent --FilteredNetMHC MouseProteinsTenMersDbTwoPercent --FilteredNetMHC MouseProteinsElevenMersDbTwoPercent

python CreatTargetSet ContaminantTest CombinedOnePercent --FilteredNetMHC MouseProteinsEightMersKbOnePercent --FilteredNetMHC MouseProteinsNineMersKbOnePercent --FilteredNetMHC MouseProteinsTenMersKbOnePercent --FilteredNetMHC MouseProteinsElevenMersKbOnePercent --FilteredNetMHC MouseProteinsEightMersDbOnePercent --FilteredNetMHC MouseProteinsNineMersDbOnePercent --FilteredNetMHC MouseProteinsTenMersDbOnePercent --FilteredNetMHC MouseProteinsElevenMersDbOnePercent

python AddContaminantFile.py ContaminantTest FASTA tests/contaminant_test/contaminants.fasta TestContaminantSetFASTANoLengths
python CreateTargetSet.py ContaminantTest Combined --PeptideList MouseProteinNineMers --PeptideList MouseProteinEightMers --PeptideList MouseProteinTenMers --PeptideList MouseProteinElevenMers

python CreateTideIndex.py ContaminantTest TargetSet Combined CombinedIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set TestContaminantSetFASTANoLengths
python CreateTideIndex.py ContaminantTest TargetSet CombinedTwoPercent CombinedTwoPercentIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set TestContaminantSetFASTANoLengths
python CreateTideIndex.py ContaminantTest TargetSet CombinedOnePercent CombinedOnePercentIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set TestContaminantSetFASTANoLengths

#python RunTideSearch.py ContaminantTest Y3MGF MiniTargetSetIndex MiniTargetSearch --param_file tide_search --param_file default_search_params

#python RunPercolator.py ContaminantTest tide MiniTargetSearch MiniTargetSearchPercolator --param_file default_percolator_params
#python FilterQValue.py ContaminantTest percolator MiniTargetSearchPercolator 0.5 MiniTargetSearchPercolatorFiftyPercent
#python ExportPeptides.py ContaminantTest FilteredSearchResult MiniTargetSearchPercolatorFiftyPercent tests/contaminant_test/percolator_peptides.txt

#python AddContaminantFile.py ContaminantTest FASTA tests/contaminant_test/contaminants.fasta TestContaminantSetFASTA 8 9 10 11
#python AddContaminantFile.py ContaminantTest FASTA tests/contaminant_test/contaminants.fasta TestContaminantSetFASTANoLengths
#python AddContaminantFile.py ContaminantTest peptides tests/contaminant_test/contaminants.txt TestContaminantSetPeptides 8 9 10 11
#python AddContaminantFile.py ContaminantTest peptides tests/contaminant_test/contaminants.txt TestContaminantSetPeptidesNoLengths


#python CreateTideIndex.py ContaminantTest TargetSet MiniTargetSet MiniTargetSetWithContaminantsIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set TestContaminantSetFASTA
#python CreateTideIndex.py ContaminantTest TargetSet MiniTargetSet MiniTargetSetWithContaminantsIndexTwo --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set TestContaminantSetFASTANoLengths
#python CreateTideIndex.py ContaminantTest TargetSet MiniTargetSet MiniTargetSetWithContaminantsIndexThree --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set TestContaminantSetPeptides
#python CreateTideIndex.py ContaminantTest TargetSet MiniTargetSet MiniTargetSetWithContaminantsIndexFour --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set TestContaminantSetPeptidesNoLengths
#python RunTideSearch.py ContaminantTest Y3MGF MiniTargetSetWithContaminantsIndexThree MiniTargetSearchWithContaminantsThree --param_file tide_search --param_file default_search_params
#python RunPercolator.py ContaminantTest tide MiniTargetSearchWithContaminantsThree MiniTargetSearchWithContaminantsPercolatorThree --param_file default_percolator_params
#python FilterQValue.py ContaminantTest percolator MiniTargetSearchWithContaminantsPercolatorThree 0.5 MiniTargetSearchPercolatorWithContaminantsFiftyPercentThree
#python ExportPeptides.py ContaminantTest FilteredSearchResult MiniTargetSearchPercolatorWithContaminantsFiftyPercentThree tests/contaminant_test/percolator_peptides.txt --contaminants tests/contaminant_test/with_contaminants_output.txt


#python CreateMSGFPlusIndex.py ContaminantTest TargetSet MiniTargetSet MiniTargetSetIndexMSGF
#python RunMSGFPlusSearch.py ContaminantTest Y3MGF MiniTargetSetIndexMSGF MiniTargetSetMSGFSearch --thread 2
#python FilterQValue.py ContaminantTest msgf MiniTargetSetMSGFSearch 0.6 MiniTargetSetMSGFSearchFiltered
#python ExportPeptides.py ContaminantTest FilteredSearchResult MiniTargetSetMSGFSearchFiltered tests/contaminant_test/msgf_peptides.txt
