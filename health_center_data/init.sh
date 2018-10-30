cd ..
python3 Initialize.py HealthCenter murphy_replication/config.ini ~/unimod.xml
python3 AddParamFile.py HealthCenter tide-search murphy_replication/tide_search.params default_search_params
python3 AddParamFile.py HealthCenter percolator murphy_replication/percolator.params default_percolator_params
python3 AddMGF.py HealthCenter /import3/MassSpec/PRAMOD/E.G7-OVA/Aug7_2018/jlb20180807_SKarandikar_20180806EG7prep.mgf PrepMGF
python3 AddMGF.py HealthCenter /import3/MassSpec/PRAMOD/E.G7-OVA/Aug7_2018/jlb20180807_SKarandikar_Srivastava_EG7_50ng_MHC1peptides_1uL_60min_Wat25cmBEH_run2.mgf Run2MGF

python3 AddFASTA.py HealthCenter health_center_data/mutated_mouse_proteome.fasta MouseProteins
python3 KChop.py HealthCenter MouseProteins 8 MouseProteinEightMers
python3 KChop.py HealthCenter MouseProteins 9 MouseProteinNineMers
python3 KChop.py HealthCenter MouseProteins 10 MouseProteinTenMers
python3 KChop.py HealthCenter MouseProteins 11 MouseProteinElevenMers
python3 AddHLA.py HealthCenter H-2-Kb
python3 AddHLA.py HealthCenter H-2-Db
python3 AddContaminantFile.py HealthCenter FASTA health_center_data/contaminants.fasta JeremyContaminants 8 9 10 11

