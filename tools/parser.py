from tools import fetch_files, pdb
from IPython import embed
import os


class InputParams:
    def __init__(self, pdb_file, sequence_file, alignment_format, chain_id, threshold):
        self.pdb_file = pdb_file
        self.sequence_file = sequence_file
        self.alignment_format = alignment_format
        self.chain_id = chain_id
        self.threshold = threshold

    def print_args(self):
        print(
            self.pdb_file,
            self.sequence_file,
            self.chain_id,
            self.alignment_format,
            self.threshold)


def run(argv,main_dir):
    if argv.pdb_id is not None:
        """
        If you choose id, then the script auto-download the PDB and Sequence (FASTA format).
        If you specify chain id, then the PDB will contain only the residues with that chain id
        """
        pdb_file = fetch_files.fetch_pdb(argv.pdb_id, argv.chain_id,main_dir)
        sequence_file = fetch_files.fetch_sequence(argv.pdb_id)
        alignment_format = "FASTA"
    else:
        """
        The pdb Object can get information with three different inputs
        from url, from file and from string
        More details in the pdb.py 
        """
        pdb_file = pdb.from_file(argv.pdb, name=os.path.basename(argv.pdb).split(".")[0],main_dir=main_dir)
        sequence_file = open(argv.seq, "r").read()
        alignment_format = argv.al

    chain_id = argv.chain_id
    """
    I don't know what to do if you don't specify the chain id
    Here I use the id of the larger chain
    """
    if chain_id is None:
        chain_id = pdb_file.get_larger_chain()

    threshold = argv.threshold

    input_params = InputParams(pdb_file,
                               sequence_file,
                               alignment_format,
                               chain_id,
                               threshold)

    return input_params
