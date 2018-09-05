cd ..

export HealthCenter=/data1/jordan/PipelineProjects/HealthCenter
echo "Going to do Tide searches"

#python3 RunTideSearch.py $HealthCenter PrepMGF CombinedTwoPercentTideIndex CombinedTwoPercentTide_Prep --param_file default_search_params

#python3 RunTideSearch.py $HealthCenter PrepMGF CombinedOnePercentTideIndex CombinedOnePercentTide_Prep --param_file default_search_params

#python3 RunTideSearch.py $HealthCenter PrepMGF CombinedTideIndex CombinedTide_Prep --param_file default_search_params

#python3 RunTideSearch.py $HealthCenter Run2MGF CombinedTwoPercentTideIndex CombinedTwoPercentTide_Run2 --param_file default_search_params

#python3 RunTideSearch.py $HealthCenter Run2MGF CombinedOnePercentTideIndex CombinedOnePercentTide_Run2 --param_file default_search_params

#python3 RunTideSearch.py $HealthCenter Run2MGF CombinedTideIndex CombinedTide_Run2 --param_file default_search_params

echo "Going to do MSGF+ searches"

#python3 RunMSGFPlusSearch.py $HealthCenter PrepMGF CombinedTwoPercentMSGFIndex CombinedTwoPercentMSGF_Prep  --memory 30000

#python3 RunMSGFPlusSearch.py $HealthCenter PrepMGF CombinedOnePercentMSGFIndex CombinedOnePercentMSGF_Prep --memory 30000

#python3 RunMSGFPlusSearch.py $HealthCenter PrepMGF CombinedMSGFIndexTwo CombinedMSGF_PrepTwo --memory 30000

#python3 RunMSGFPlusSearch.py $HealthCenter Run2MGF CombinedTwoPercentMSGFIndex CombinedTwoPercentMSGF_Run2 --memory 30000

#python3 RunMSGFPlusSearch.py $HealthCenter Run2MGF CombinedOnePercentMSGFIndex CombinedOnePercentMSGF_Run2 --memory 30000

#python3 RunMSGFPlusSearch.py $HealthCenter Run2MGF CombinedMSGFIndexTwo CombinedMSGF_Run2Two --memory 30000



python3 RunTideSearch.py $HealthCenter PrepMGF CombinedTwoPercentTideIndexReverseForDecoys CombinedTwoPercentTide_PrepReverseForDecoys --param_file default_search_params

python3 RunTideSearch.py $HealthCenter PrepMGF CombinedOnePercentTideIndexReverseForDecoys CombinedOnePercentTide_PrepReverseForDecoys --param_file default_search_params

python3 RunTideSearch.py $HealthCenter PrepMGF CombinedTideIndexReverseForDecoys CombinedTide_PrepReverseForDecoys --param_file default_search_params


