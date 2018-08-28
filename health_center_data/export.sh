cd ..

NAME="CombinedTwoPercentTide_Prep_percolator_filtered"
python3 ExportPeptides.py HealthCenter FilteredSearchResult $(NAME) health_center_data/$(NAME)/peptides.txt --contaminants health_center_data/$(NAME)/contaminants.txt

NAME="CombinedOnePercentTide_Prep_percolator_filtered"

python3 ExportPeptides.py HealthCenter FilteredSearchResult $(NAME) health_center_data/$(NAME)/peptides.txt --contaminants health_center_data/$(NAME)/contaminants.txt

NAME="CombinedTide_Prep_percolator_filtered"
python3 ExportPeptides.py HealthCenter FilteredSearchResult $(NAME) health_center_data/$(NAME)/peptides.txt --contaminants health_center_data/$(NAME)/contaminants.txt

NAME="CombinedTwoPercentTide_Run2_percolator_filtered"

python3 ExportPeptides.py HealthCenter FilteredSearchResult $(NAME) health_center_data/$(NAME)/peptides.txt --contaminants health_center_data/$(NAME)/contaminants.txt


NAME="CombinedOnePercentTide_Run2_percolator_filtered"
python3 ExportPeptides.py HealthCenter FilteredSearchResult $(NAME) health_center_data/$(NAME)/peptides.txt --contaminants health_center_data/$(NAME)/contaminants.txt

NAME="CombinedTide_Run2_percolator_filtered"
python3 ExportPeptides.py HealthCenter FilteredSearchResult $(NAME) health_center_data/$(NAME)/peptides.txt --contaminants health_center_data/$(NAME)/contaminants.txt

NAME="CombinedTwoPercentMSGF_Prep_percolator_filtered"
python3 ExportPeptides.py HealthCenter FilteredSearchResult $(NAME) health_center_data/$(NAME)/peptides.txt --contaminants health_center_data/$(NAME)/contaminants.txt


NAME="CombinedOnePercentMSGF_Prep_percolator_filtered"
python3 ExportPeptides.py HealthCenter FilteredSearchResult $(NAME) health_center_data/$(NAME)/peptides.txt --contaminants health_center_data/$(NAME)/contaminants.txt


NAME="CombinedMSGF_Run2_percolator_filtered"
python3 ExportPeptides.py HealthCenter FilteredSearchResult $(NAME) health_center_data/$(NAME)/peptides.txt --contaminants health_center_data/$(NAME)/contaminants.txt


NAME="CombinedOnePercentMSGF_Run2_percolator_filtered"
python3 ExportPeptides.py HealthCenter FilteredSearchResult $(NAME) health_center_data/$(NAME)/peptides.txt --contaminants health_center_data/$(NAME)/contaminants.txt


NAME="CombinedTwoPercentMSGF_Run2_percolator_filtered"
python3 ExportPeptides.py HealthCenter FilteredSearchResult $(NAME) health_center_data/$(NAME)/peptides.txt --contaminants health_center_data/$(NAME)/contaminants.txt



NAME="CombinedMSGF_Prep_percolator_filtered"
python3 ExportPeptides.py HealthCenter FilteredSearchResult $(NAME) health_center_data/$(NAME)/peptides.txt --contaminants health_center_data/$(NAME)/contaminants.txt

