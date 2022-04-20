import os

from tools import sequence_convert, whiscy_hssp, whiscy_pdbutil


class SeqFile:
    def __init__(self, string, name, seq_dir, seq_format, hssp_dir=None):
        self.as_string = string
        self.name = name
        self.seq_dir = seq_dir
        self.format = seq_format
        self.hssp_dir = hssp_dir


def save_seq_to_temp_dir(main_dir, seq_string, name, seq_format):
    temp_dir = os.path.join(main_dir, "temp")
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    if seq_format == "PHYLIP":
        seq_file = "{}.{}".format(name, "phylseq")
    else:
        seq_file = "{}.{}".format(name, seq_format)
    seq_dir = os.path.join(temp_dir, seq_file)
    if not os.path.exists(seq_dir):
        save_file = open(seq_dir, "w")
        save_file.write(seq_string)
        save_file.close()
    return seq_dir


def from_file(seq_dir, name, main_dir, seq_format, pdb_file, chain):
    print("Converting the Sequence..." + os.linesep)
    # Convert the sequence to PHYLSEQ (WHISCY)
    phylip_dir = sequence_convert.run(
        seq_dir, seq_format, pdb_file.pdb_dir, chain, main_dir
    )
    seq_string = open(phylip_dir, "rb").read().decode("UTF-8")
    seq_object = SeqFile(seq_string, name, phylip_dir, "PHYLIP")
    return seq_object


def fetch_from_id(pdb_id, main_dir, pdb_file, chain):
    master_sequence = whiscy_pdbutil.get_pdb_sequence(pdb_file.pdb_dir, chain)
    # Download HSSP sequence file
    name = os.path.basename(main_dir)[:-5]
    (hssp_seq, hssp_dir) = whiscy_hssp.get_from_web(pdb_id, main_dir)
    # Convert to PHYLSEQ (WHISCY)

    seq_name = f"{name}_final_phylip.phylseq"
    phylip_dir, phylip_seq = whiscy_hssp.hssp_file_to_phylip(
        hssp_dir, seq_name, chain, master_sequence, main_dir
    )
    print("HSSP is converted to phylseq and saved to temp folder" + os.linesep)
    seq_object = SeqFile(phylip_seq, seq_name, phylip_dir, "PHYLIP")
    return seq_object
