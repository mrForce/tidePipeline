all: fasta_to_peptide_list

fasta_to_peptide_list: fasta_to_peptide_list.o
	g++ fasta_to_peptide_list.o -o fasta_to_peptide_list
fasta_to_peptide_list.o: fasta_to_peptide_list.cpp
	g++ -c fasta_to_peptide_list.cpp

clean:
	rm *.o fasta_to_peptide_list
