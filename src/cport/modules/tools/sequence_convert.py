import json
import os

from Bio import SearchIO
from Bio.Align.Applications import MuscleCommandline
from Bio.Blast import NCBIWWW

from . import whiscy_pdbutil


class SequenceConverter:
    def __init__(self, sequence_dict, master_sequence=None):
        self.dic = sequence_dict
        self.master_sequence = master_sequence

    def n_seq(self):
        return len(self.dic)

    def add_master_sequence(self, pdb_file, chain):
        self.master_sequence = whiscy_pdbutil.get_pdb_sequence(pdb_file, chain)

    def dic_to_fasta(self):
        total_seq = ""
        for seq_name in self.dic.keys():
            name = f">{str(seq_name)}" + os.linesep
            seq = ""
            for i in range(0, len(self.dic[seq_name]), 60):
                line = f"{self.dic[seq_name][i:i+60]}" + os.linesep
                seq = seq + line
            total_seq = total_seq + name + seq
        return total_seq

    def save_fasta_msa_alignment(self, main_dir):
        tools_dir = os.path.dirname(os.path.realpath(__file__))
        cport_dir = os.path.dirname(tools_dir)
        config_dir = os.path.join(cport_dir, "config.json")
        json_file = json.load(open(config_dir, "r"))
        muscle_dir = json_file["MUSCLE"]
        temp_dir = os.path.join(main_dir, "temp")
        fasta_text = self.dic_to_fasta()
        fin_dir = os.path.join(temp_dir, "temp_fasta.fasta")
        fout_dir = os.path.join(temp_dir, "muscle_mca.fasta")
        with open(fin_dir, "w") as f:
            f.write(fasta_text)
        f.close()
        muscle_cline = MuscleCommandline(muscle_dir, input=fin_dir, out=fout_dir)
        muscle_cline()
        return fout_dir

    def save_final_phylip(self, name):
        n_seq = len(self.dic) + 1
        seq_length = len(self.master_sequence)
        first_line = f"{n_seq} {seq_length}" + os.linesep
        master_line = f"{'MASTER':10s}{self.master_sequence}" + os.linesep
        rest_seq = first_line + master_line
        for seq_name in self.dic.keys():
            line = f"{str(seq_name):10s}{self.dic[seq_name]}" + os.linesep
            rest_seq = rest_seq + line
        with open(name, "w") as f:
            f.write(rest_seq)
        f.close()
        return name

    def all_same_length(self):
        if len(set([len(s) for s in self.dic.values()])) == 1:
            return True
        else:
            return False


def from_clustal(seq_file):
    f = open(seq_file, "r").read()
    f = f.rstrip()
    f = f.split(os.linesep)
    for i, line in enumerate(f):
        if len(line) == 86:
            first_line = i
            break
    clean_file = f[first_line:]
    clean_file.append("")
    final_list = []
    temp_list = []
    for seq in clean_file:
        if seq != "":
            temp_list.append(seq)
        else:
            final_list.append(temp_list)
            temp_list = []
    new_dic = {}
    for i, final_seq in enumerate(zip(*final_list)):
        seq = "".join([i[36:] for i in final_seq])
        name = i + 1
        new_dic[name] = seq
    return SequenceConverter(new_dic)


def from_fasta(seq_file):
    f = open(seq_file, "r").readlines()
    new_dic = {}
    i = 0
    for line in f:
        if line.startswith(">"):
            i += 1
            name = i
            seq = ""
        else:
            seq = line
        if name in new_dic.keys():
            new_dic[name] = new_dic[name] + seq.strip()
        else:
            new_dic[name] = seq.strip()
    return SequenceConverter(new_dic)


def from_maf(seq_file):
    f = open(seq_file, "r").readlines()
    new_dic = {}
    i = 0
    for line in f:
        if line.startswith("s"):
            i += 1
            split_line = line.split()
            name = i
            seq = split_line[-1]
            new_dic[name] = seq
    return SequenceConverter(new_dic)


def from_phylip(seq_file):
    f = open(seq_file, "r").read()
    f = f.strip()
    f = f.split(os.linesep)
    clean_file = f[1:]
    clean_file.append("")
    final_list = []
    temp_list = []
    for seq in clean_file:
        if seq != "":
            temp_list.append(seq)
        else:
            final_list.append(temp_list)
            temp_list = []

    new_dic = {}
    for i, final_seq in enumerate(zip(*final_list)):
        seq = "".join(["".join(i[11:].split()) for i in final_seq])
        name = i + 1
        new_dic[name] = seq
    return SequenceConverter(new_dic)


def from_xml(xml_file):
    blast_xml = SearchIO.read(xml_file, "blast-xml")
    new_dic = {}
    for i, hit in enumerate(blast_xml):
        name = i + 1
        new_dic[name] = str(hit[0].hit.seq)
    return SequenceConverter(new_dic)


def run(seq_dir, seq_format, pdb_file, chain, main_dir):
    # Takes the Sequence and store it in a dictionary
    try:
        if seq_format == "FASTA":
            seq = from_fasta(seq_dir)
        elif seq_format == "CLUSTAL":
            seq = from_clustal(seq_dir)
        elif seq_format == "MAF":
            seq = from_maf(seq_dir)
        elif seq_format == "PHYLIP":
            seq = from_phylip(seq_dir)
        else:
            raise AssertionError("Sequence Format not supported")
    except Exception:
        raise AssertionError("Failed : Sequence Format not supported")

    n_seq = seq.n_seq()

    print(
        f"Sequence format: {seq_format} and number of sequences: {n_seq}" + os.linesep
    )

    # If the number of sequence is larger than 1
    if n_seq > 1:
        print("Aligning Sequences... " + os.linesep)
        # Align the sequence
        if seq.all_same_length():
            final_seq = seq
        else:
            mca_fasta = seq.save_fasta_msa_alignment(main_dir)
            print("Sequences aligned and saved to temp folder " + os.linesep)
            # Return a FASTA sequence
            final_seq = from_fasta(mca_fasta)

    # IF there is only one sequence
    elif n_seq == 1:
        print("Blast sequence...." + os.linesep)
        # Blast to get the multi sequence alignment
        results_handle = NCBIWWW.qblast(
            "blastp", "nr", seq.dic_to_fasta(), hitlist_size=100
        )

        temp_dir = os.path.join(main_dir, "temp")
        xml_results = os.path.join(temp_dir, "results.xml")
        with open(xml_results, "w") as save_file:
            blast_results = results_handle.read()
            save_file.write(blast_results)
            save_file.close()
        print("XML file saved to the temp folder" + os.linesep)

        # Dictionary with sequences, from the blast result (XML)
        seq = from_xml(xml_results)
        print("Aligning Sequences... " + os.linesep)

        # Align the sequences
        mca_fasta = seq.save_fasta_msa_alignment(main_dir)
        print("Sequences aligned and saved to temp folder" + os.linesep)

        # Return a FASTA sequence
        final_seq = from_fasta(mca_fasta)
    else:
        raise AssertionError("No sequence found")

    # Add the master sequence (Need for WHISCY)
    final_seq.add_master_sequence(pdb_file, chain)

    temp_dir = os.path.join(main_dir, "temp")
    final_dir = os.path.join(
        temp_dir, f"{os.path.basename(main_dir)[:-5]}_final_phylip.phylseq"
    )
    final_seq.save_final_phylip(final_dir)
    # Return the final PHYLSEQ FOR WHISCY
    return final_dir
