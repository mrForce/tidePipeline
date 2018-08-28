cd ..

echo "Going to do Tide searches"

python3 RunTideSearch.py PrepMGF CombinedTwoPercentTideIndex CombinedTwoPercentTide_Prep --param_file default_search_params

python3 RunTideSearch.py PrepMGF CombinedOnePercentTideIndex CombinedOnePercentTide_Prep --param_file default_search_params

python3 RunTideSearch.py PrepMGF CombinedTideIndex CombinedTide_Prep --param_file default_search_params

python3 RunTideSearch.py Run2MGF CombinedTwoPercentTideIndex CombinedTwoPercentTide_Run2 --param_file default_search_params

python3 RunTideSearch.py Run2MGF CombinedOnePercentTideIndex CombinedOnePercentTide_Run2 --param_file default_search_params

python3 RunTideSearch.py Run2MGF CombinedTideIndex CombinedTide_Run2 --param_file default_search_params

echo "Going to do MSGF+ searches"

python3 RunMSGFPlusSearch.py PrepMGF CombinedTwoPercentMSGFIndex CombinedTwoPercentMSGF_Prep  --memory 30000

python3 RunMSGFPlusSearch.py PrepMGF CombinedOnePercentMSGFIndex CombinedOnePercentMSGF_Prep --memory 30000

python3 RunMSGFPlusSearch.py PrepMGF CombinedMSGFIndex CombinedMSGF_Prep --memory 30000

python3 RunMSGFPlusSearch.py Run2MGF CombinedTwoPercentMSGFIndex CombinedTwoPercentMSGF_Run2 --memory 30000

python3 RunMSGFPlusSearch.py Run2MGF CombinedOnePercentMSGFIndex CombinedOnePercentMSGF_Run2 --memory 30000

python3 RunMSGFPlusSearch.py Run2MGF CombinedMSGFIndex CombinedMSGF_Run2 --memory 30000



