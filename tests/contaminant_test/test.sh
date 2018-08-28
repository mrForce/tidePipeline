cd ../..
python3 Initialize.py ContaminantTest murphy_replication/config.ini ~/unimod.xml
python3 AddParamFile.py ContaminantTest tide-search murphy_replication/tide_search.params default_search_params
python3 AddParamFile.py ContaminantTest percolator murphy_replication/percolator.params default_percolator_params
python3 AddMGF.py ContaminantTest ~/Downloads/160127_609_015_EL4_Y3.mgf Y3MGF
python3 AddHLA.py ContaminantTest H-2-Kb
python3 AddHLA.py ContaminantTest H-2-Db
python3 AddFASTA.py ContaminantTest ~/Downloads/first_mouse_protein.fasta MouseProteins
python3 KChop.py ContaminantTest MouseProteins 9 MouseProteinNineMers
python3 KChop.py ContaminantTest MouseProteins 8 MouseProteinEightMers
python3 KChop.py ContaminantTest MouseProteins 10 MouseProteinTenMers
python3 KChop.py ContaminantTest MouseProteins 11 MouseProteinElevenMers
echo "GOING TO START NETMHC"
python3 RunNetMHC.py ContaminantTest MouseProteinEightMers H-2-Kb 2 MouseProteinsEightMersKbTwoPercent 
python3 RunNetMHC.py ContaminantTest MouseProteinEightMers H-2-Kb 1 MouseProteinsEightMersKbOnePercent
python3 RunNetMHC.py ContaminantTest MouseProteinNineMers H-2-Kb 2 MouseProteinsNineMersKbTwoPercent
python3 RunNetMHC.py ContaminantTest MouseProteinNineMers H-2-Kb 1 MouseProteinsNineMersKbOnePercent
python3 RunNetMHC.py ContaminantTest MouseProteinTenMers H-2-Kb 2 MouseProteinsTenMersKbTwoPercent
python3 RunNetMHC.py ContaminantTest MouseProteinTenMers H-2-Kb 1 MouseProteinsTenMersKbOnePercent
python3 RunNetMHC.py ContaminantTest MouseProteinElevenMers H-2-Kb 2 MouseProteinsElevenMersKbTwoPercent
python3 RunNetMHC.py ContaminantTest MouseProteinElevenMers H-2-Kb 1 MouseProteinsElevenMersKbOnePercent

python3 RunNetMHC.py ContaminantTest MouseProteinEightMers H-2-Db 2 MouseProteinsEightMersDbTwoPercent
python3 RunNetMHC.py ContaminantTest MouseProteinEightMers H-2-Db 1 MouseProteinsEightMersDbOnePercent
python3 RunNetMHC.py ContaminantTest MouseProteinNineMers H-2-Db 2 MouseProteinsNineMersDbTwoPercent
python3 RunNetMHC.py ContaminantTest MouseProteinNineMers H-2-Db 1 MouseProteinsNineMersDbOnePercent
python3 RunNetMHC.py ContaminantTest MouseProteinTenMers H-2-Db 2 MouseProteinsTenMersDbTwoPercent
python3 RunNetMHC.py ContaminantTest MouseProteinTenMers H-2-Db 1 MouseProteinsTenMersDbOnePercent
python3 RunNetMHC.py ContaminantTest MouseProteinElevenMers H-2-Db 2 MouseProteinsElevenMersDbTwoPercent
python3 RunNetMHC.py ContaminantTest MouseProteinElevenMers H-2-Db 1 MouseProteinsElevenMersDbOnePercent

python3 CreatTargetSet ContaminantTest CombinedTwoPercent --FilteredNetMHC MouseProteinsEightMersKbTwoPercent --FilteredNetMHC MouseProteinsNineMersKbTwoPercent --FilteredNetMHC MouseProteinsTenMersKbTwoPercent --FilteredNetMHC MouseProteinsElevenMersKbTwoPercent --FilteredNetMHC MouseProteinsEightMersDbTwoPercent --FilteredNetMHC MouseProteinsNineMersDbTwoPercent --FilteredNetMHC MouseProteinsTenMersDbTwoPercent --FilteredNetMHC MouseProteinsElevenMersDbTwoPercent

python3 CreatTargetSet ContaminantTest CombinedOnePercent --FilteredNetMHC MouseProteinsEightMersKbOnePercent --FilteredNetMHC MouseProteinsNineMersKbOnePercent --FilteredNetMHC MouseProteinsTenMersKbOnePercent --FilteredNetMHC MouseProteinsElevenMersKbOnePercent --FilteredNetMHC MouseProteinsEightMersDbOnePercent --FilteredNetMHC MouseProteinsNineMersDbOnePercent --FilteredNetMHC MouseProteinsTenMersDbOnePercent --FilteredNetMHC MouseProteinsElevenMersDbOnePercent

python3 AddContaminantFile.py ContaminantTest FASTA tests/contaminant_test/contaminants.fasta TestContaminantSetFASTANoLengths
python3 CreateTargetSet.py ContaminantTest Combined --PeptideList MouseProteinNineMers --PeptideList MouseProteinEightMers --PeptideList MouseProteinTenMers --PeptideList MouseProteinElevenMers

python3 CreateTideIndex.py ContaminantTest TargetSet Combined CombinedIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set TestContaminantSetFASTANoLengths
python3 CreateTideIndex.py ContaminantTest TargetSet CombinedTwoPercent CombinedTwoPercentIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set TestContaminantSetFASTANoLengths
python3 CreateTideIndex.py ContaminantTest TargetSet CombinedOnePercent CombinedOnePercentIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set TestContaminantSetFASTANoLengths

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
