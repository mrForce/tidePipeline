python3 CreateTargetSet.py HealthCenter CombinedTwoPercent --FilteredNetMHC MouseProteinsEightMersKbTwoPercent --FilteredNetMHC MouseProteinsNineMersKbTwoPercent --FilteredNetMHC MouseProteinsTenMersKbTwoPercent --FilteredNetMHC MouseProteinsElevenMersKbTwoPercent --FilteredNetMHC MouseProteinsEightMersDbTwoPercent --FilteredNetMHC MouseProteinsNineMersDbTwoPercent --FilteredNetMHC MouseProteinsTenMersDbTwoPercent --FilteredNetMHC MouseProteinsElevenMersDbTwoPercent 

python3 CreateTideIndex.py HealthCenter TargetSet CombinedTwoPercent CombinedTwoPercentTideIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set JeremyContaminants

python3 CreateMSGFPlusIndex.py HealthCenter TargetSet CombinedTwoPercent CombinedTwoPercentMSGFIndex --contaminant_set JeremyContaminants --memory 30000

python3 CreateTargetSet.py HealthCenter CombinedOnePercent --FilteredNetMHC MouseProteinsEightMersKbOnePercent --FilteredNetMHC MouseProteinsNineMersKbOnePercent --FilteredNetMHC MouseProteinsTenMersKbOnePercent --FilteredNetMHC MouseProteinsElevenMersKbOnePercent --FilteredNetMHC MouseProteinsEightMersDbOnePercent --FilteredNetMHC MouseProteinsNineMersDbOnePercent --FilteredNetMHC MouseProteinsTenMersDbOnePercent --FilteredNetMHC MouseProteinsElevenMersDbOnePercent 

python3 CreateTideIndex.py HealthCenter TargetSet CombinedOnePercent CombinedOnePercentTideIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set JeremyContaminants

python3 CreateMSGFPlusIndex.py HealthCenter TargetSet CombinedOnePercent CombinedOnePercentMSGFIndex --contaminant_set JeremyContaminants --memory 30000

python3 CreateTargetSet.py HealthCenter Combined --PeptideList MouseProteinNineMers --PeptideList MouseProteinEightMers --PeptideList MouseProteinTenMers --PeptideList MouseProteinElevenMers

python3 CreateTideIndex.py HealthCenter TargetSet Combined CombinedTideIndex --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set JeremyContaminants

python3 CreateMSGFPlusIndex.py HealthCenter TargetSet CombinedOnePercent CombinedMSGFIndex --contaminant_set JeremyContaminants --memory 30000


