
cd ..
export HealthCenter=/data1/jordan/PipelineProjects/HealthCenter
NAME="CombinedTwoPercentTide_Prep_percolator_filtered_five_percent_fdr_three"
#mkdir health_center_data/$NAME
#python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedOnePercentTide_Prep_percolator_filtered_five_percent_fdr_three"
#mkdir health_center_data/$NAME
#python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedTide_Prep_percolator_filtered_five_percent_fdr_three"
#mkdir health_center_data/$NAME
#python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedTwoPercentTide_Run2_percolator_filtered_five_percent_fdr_three"
#mkdir health_center_data/$NAME
#python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt


NAME="CombinedOnePercentTide_Run2_percolator_filtered_five_percent_fdr_three"
#mkdir health_center_data/$NAME
#python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedTide_Run2_percolator_filtered_five_percent_fdr_three"
#mkdir health_center_data/$NAME
#python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedTwoPercentMSGF_Prep_percolator_filtered_five_percent_fdr_three"
#mkdir health_center_data/$NAME
#python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt


NAME="CombinedOnePercentMSGF_Prep_percolator_filtered_five_percent_fdr_three"
#mkdir health_center_data/$NAME
#python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt


NAME="CombinedMSGF_Run2Two_percolator_filtered_five_percent_fdr_three"
#mkdir health_center_data/$NAME
#python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt


NAME="CombinedOnePercentMSGF_Run2_percolator_filtered_five_percent_fdr_three"
#mkdir health_center_data/$NAME
#python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt


NAME="CombinedTwoPercentMSGF_Run2_percolator_filtered_five_percent_fdr_three"
#mkdir health_center_data/$NAME
#python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt



NAME="CombinedMSGF_PrepTwo_percolator_filtered_five_percent_fdr_three"
#mkdir health_center_data/$NAME
#python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt


NAME="CombinedTwoPercentTide_Prep_percolator_with_param_five_percent_fdr"
mkdir health_center_data/$NAME
python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedOnePercentTide_Prep_percolator_with_param_five_percent_fdr"
mkdir health_center_data/$NAME
python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedTide_Prep_percolator_with_param_five_percent_fdr"
mkdir health_center_data/$NAME
python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt




NAME="CombinedTwoPercentTide_PrepReverseForDecoys_percolator_five_percent_fdr"
mkdir health_center_data/$NAME
python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedOnePercentTide_PrepReverseForDecoys_percolator_five_percent_fdr"
mkdir health_center_data/$NAME
python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

NAME="CombinedTide_PrepReverseForDecoys_percolator_five_percent_fdr"
mkdir health_center_data/$NAME
python3 ExportPeptides.py $HealthCenter FilteredSearchResult $NAME health_center_data/$NAME/peptides.txt --contaminants health_center_data/$NAME/contaminants.txt

