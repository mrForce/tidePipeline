all: fasta_to_peptide_list

fasta_to_peptide_list: fasta_to_peptide_list.o
	g++  -O3 fasta_to_peptide_list.o -o fasta_to_peptide_list
fasta_to_peptide_list.o: fasta_to_peptide_list.cpp
	g++ -O3 -c fasta_to_peptide_list.cpp

clean:
	rm *.o fasta_to_peptide_list
