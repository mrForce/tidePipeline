cd ..

HealthCenter=/data1/jordan/PipelineProjects/HealthCenter



python3 CreateTideIndex.py $HealthCenter TargetSet CombinedTwoPercent CombinedTwoPercentTideIndex_shuffled_decoys --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set JeremyContaminants 






python3 CreateTideIndex.py $HealthCenter TargetSet CombinedOnePercent CombinedOnePercentTideIndex_shuffled_decoys --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set JeremyContaminants







python3 CreateTideIndex.py $HealthCenter TargetSet Combined CombinedTideIndex_shuffled_decoys --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme --contaminant_set JeremyContaminants






