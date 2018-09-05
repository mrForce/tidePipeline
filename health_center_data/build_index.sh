cd ..

HealthCenter=/data1/jordan/PipelineProjects/HealthCenter

#python3 CreateTargetSet.py $HealthCenter CombinedTwoPercent --FilteredNetMHC MouseProteinsEightMersKbTwoPercent --FilteredNetMHC MouseProteinsNineMersKbTwoPercent --FilteredNetMHC MouseProteinsTenMersKbTwoPercent --FilteredNetMHC MouseProteinsElevenMersKbTwoPercent --FilteredNetMHC MouseProteinsEightMersDbTwoPercent --FilteredNetMHC MouseProteinsNineMersDbTwoPercent --FilteredNetMHC MouseProteinsTenMersDbTwoPercent --FilteredNetMHC MouseProteinsElevenMersDbTwoPercent 

#python3 CreateTideIndex.py $HealthCenter TargetSet CombinedTwoPercent CombinedTwoPercentTideIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set JeremyContaminants

python3 CreateTideIndex.py $HealthCenter TargetSet CombinedTwoPercent CombinedTwoPercentTideIndexReverseForDecoys --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set JeremyContaminants --decoy-format peptide-reverse
#python3 CreateMSGFPlusIndex.py $HealthCenter TargetSet CombinedTwoPercent CombinedTwoPercentMSGFIndex --contaminantSet JeremyContaminants --memory 30000

#python3 CreateTargetSet.py $HealthCenter CombinedOnePercent --FilteredNetMHC MouseProteinsEightMersKbOnePercent --FilteredNetMHC MouseProteinsNineMersKbOnePercent --FilteredNetMHC MouseProteinsTenMersKbOnePercent --FilteredNetMHC MouseProteinsElevenMersKbOnePercent --FilteredNetMHC MouseProteinsEightMersDbOnePercent --FilteredNetMHC MouseProteinsNineMersDbOnePercent --FilteredNetMHC MouseProteinsTenMersDbOnePercent --FilteredNetMHC MouseProteinsElevenMersDbOnePercent 

#python3 CreateTideIndex.py $HealthCenter TargetSet CombinedOnePercent CombinedOnePercentTideIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set JeremyContaminants

python3 CreateTideIndex.py $HealthCenter TargetSet CombinedOnePercent CombinedOnePercentTideIndexReverseForDecoys --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set JeremyContaminants --decoy-format peptide-reverse

#python3 CreateMSGFPlusIndex.py $HealthCenter TargetSet CombinedOnePercent CombinedOnePercentMSGFIndex --contaminantSet JeremyContaminants --memory 30000

#python3 CreateTargetSet.py $HealthCenter Combined --PeptideList MouseProteinNineMers --PeptideList MouseProteinEightMers --PeptideList MouseProteinTenMers --PeptideList MouseProteinElevenMers

#python3 CreateTideIndex.py $HealthCenter TargetSet Combined CombinedTideIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set JeremyContaminants

python3 CreateTideIndex.py $HealthCenter TargetSet Combined CombinedTideIndexReverseForDecoys --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set JeremyContaminants --decoy-format peptide-reverse

#python3 CreateMSGFPlusIndex.py $HealthCenter TargetSet Combined CombinedMSGFIndexTwo --contaminantSet JeremyContaminants --memory 30000


