#!/bin/bash
cd ..
python3 Initialize.py MurphyReplication murphy_replication/config.ini
python3 AddMaxQuantParamFile.py MurphyReplication  murpyh_replication/mqpar.xml MaxQuantConfig
python3 AddRAW.py MurphyReplication ~/Downloads/160127_609_015_EL4_Y3.raw Y3RAW
python3 AddRAW.py MurphyReplication ~/Downloads/160127_609_015_EL4_B22.raw B22RAW
python3 AddMGF.py MurphyReplication ~/Downloads/160127_609_015_EL4_Y3.mgf Y3MGF
python3 AddMGF.py MurphyReplication ~/Downloads/160127_609_015_EL4_B22.mgf B22MGF
python3 AddHLA.py MurphyReplication H-2-Kb
python3 AddHLA.py MurphyReplication H-2-Db
python3 AddFASTA.py MurphyReplication ~/Downloads/all_mouse_proteins.fasta MouseProteins
python3 KChop.py MurphyReplication MouseProteins 9 MouseProteinNineMers
python3 KChop.py MurphyReplication MouseProteins 8 MouseProteinEightMers
python3 KChop.py MurphyReplication MouseProteins 10 MouseProteinTenMers
python3 KChop.py MurphyReplication MouseProteins 11 MouseProteinElevenMers
