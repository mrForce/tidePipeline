#!/bin/bash

cd ..
#python3 tPipeInitialize.py testProject
#python3 tPipeAddSpecies.py testProject cow
#python3 tPipeAddHLA.py testProject BoLA-AW10 cow
#python3 tPipeAddHLA.py testProject BoLA-T2a cow
#python3 tPipeAddFASTA.py testProject ~/theileria.fasta Theileria

#python3 tPipeAddPeptideList.py testProject EightMers Theileria 8
#python3 tPipeAddPeptideList.py testProject NineMers Theileria 9
#python3 tPipeAddPeptideList.py testProject TenMers Theileria 10
#python3 tPipeAddPeptideList.py testProject ElevenMers Theileria 11
#echo "Going to create tide index"
#python3 tPipeCreateTideIndex.py testProject combined_database --netMHCFilter EightMers BoLA-AW10 2 --netMHCFilter NineMers BoLA-AW10 2 --netMHCFilter TenMers BoLA-AW10 2 --netMHCFilter ElevenMers BoLA-AW10 2 --netMHCFilter EightMers BoLA-T2a 2 --netMHCFilter NineMers BoLA-T2a 2 --netMHCFilter TenMers BoLA-T2a 2 --netMHCFilter ElevenMers BoLA-T2a 2 --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme
echo "going to add mgf"
#python3 tPipeAddMGF.py testProject "/home/jordan/HF0002_TC_1011.mgf" cows
echo "going to run search"
python3 tPipeRunTideSearch.py testProject cows combined_database CowsCombinedSearch
