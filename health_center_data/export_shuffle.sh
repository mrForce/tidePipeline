
cd ..
export HealthCenter=/data1/jordan/PipelineProjects/HealthCenter
NAME="CombinedTwoPercentTide_Prep_percolator_filtered_five_percent_fdr_shuffled_decoys"
mkdir health_center_data/$NAME
python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedOnePercentTide_Prep_percolator_filtered_five_percent_fdr_shuffled_decoys"
mkdir health_center_data/$NAME
python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedTide_Prep_percolator_filtered_five_percent_fdr_shuffled_decoys"
mkdir health_center_data/$NAME
python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedTwoPercentTide_Run2_percolator_filtered_five_percent_fdr_shuffled_decoys"
mkdir health_center_data/$NAME
python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt


NAME="CombinedOnePercentTide_Run2_percolator_filtered_five_percent_fdr_shuffled_decoys"
mkdir health_center_data/$NAME
python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedTide_Run2_percolator_filtered_five_percent_fdr_shuffled_decoys"
mkdir health_center_data/$NAME
python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

