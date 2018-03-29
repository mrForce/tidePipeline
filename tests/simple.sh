#!/bin/bash

cd ..
python tPipeInitialize.py testProject
python tPipeAddSpecies.py testProject mouse
python tPipeAddHLA.py testProject H-2-Db mouse
python tPipeAddHLA.py testProject H-2-Kb mouse
python tPipeAddFASTA.py testProject ~/tide_files/mouse_uniprot_kb.fasta MouseUniprot
python tPipeAddPeptideList.py testProject EightMers MouseUniprot 8
python tPipeAddPeptideList.py testProject NineMers MouseUniprot 9
python tPipeAddPeptideList.py testProject TenMers MouseUniprot 10
python tPipeAddPeptideList.py testProject ElevenMers MouseUniprot 11
echo "Going to create tide index"
python tPipeCreateTideIndex.py testProject combined_database --decoy-generator "~/github/crux-toolkit/test/decoy-generation-tests/shuffle" --netMHCFilter EightMers H-2-Kb 2 --netMHCFilter NineMers H-2-Kb 2 --netMHCFilter TenMers H-2-Kb 2 --netMHCFilter ElevenMers H-2-Kb 2 --netMHCFilter EightMers H-2-Db 2 --netMHCFilter NineMers H-2-Db 2 --netMHCFilter TenMers H-2-Db 2 --netMHCFilter ElevenMers H-2-Db 2 --custom-enzyme '[Z]|[Z]' --enzyme custom-enzyme
echo "going to add mgf"
python tPipeAddMGF.py testProject "/home/jforce/tide_files/160127_609_015_EL4_B22.mgf" B22
python tPipeRunTideSearch.py testProject B22 combined_database B22CombinedSearch
