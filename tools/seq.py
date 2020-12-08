from urllib import request
import numpy as np
import os
from IPython import embed
from tools import whiscy_hssp
from tools import whiscy_pdbutil
from tools import sequence_convert

class SeqFile:

    def __init__(self, string, name,seq_dir,format,hssp_dir=None):
        self.as_string = string
        self.name = name
        self.seq_dir = seq_dir
        self.format = format
        self.hssp_dir = hssp_dir

def save_seq_to_temp_dir(main_dir,seq_string,name,format):
    temp_dir = os.path.join(main_dir, "temp")
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    if format == "PHYLIP":
        seq_file = "{}.{}".format(name, "phylseq")
    else:
        seq_file = "{}.{}".format(name, format)
    seq_dir = os.path.join(temp_dir,seq_file)
    if not os.path.exists(seq_dir):
        save_file = open(seq_dir, "w")
        save_file.write(seq_string)
        save_file.close()
    return seq_dir

def from_file(seq_dir, name, main_dir,format,pdb_file,chain):
    print("Converting the Sequence... \n")
    # Convert the sequence to PHYLSEQ (WHISCY)
    phylip_dir = sequence_convert.run(seq_dir,format,pdb_file.pdb_dir,chain,main_dir)
    seq_string = open(phylip_dir, "rb").read().decode("UTF-8")
    seq_object = SeqFile(seq_string,name,phylip_dir,"PHYLIP")
    return seq_object

def from_url(seq_url, name, main_dir,format,pdb_file,chain):
    master_sequence = whiscy_pdbutil.get_pdb_sequence(pdb_file.pdb_dir,chain)
    # Download HSSP sequence file
    (hssp_seq,hssp_dir) = whiscy_hssp.get_from_web(name,main_dir)

    # Convert to PHYLSEQ (WHISCY)
    phylip_dir,phylip_seq = whiscy_hssp.hssp_file_to_phylip(hssp_dir,"{}.phylseq".format(name),chain,master_sequence,main_dir)
    print("HSSP is converted to phylseq and saved to temp folder\n")
    seq_object = SeqFile(phylip_seq, name, phylip_dir, "PHYLIP")
    return seq_object

def fetch_from_id(pdb_id,format,main_dir,pdb_file,chain):
    seq_url = "https://www.rcsb.org/fasta/entry/{}/display".format(pdb_id)
    object = from_url(seq_url,pdb_id,main_dir,format,pdb_file,chain)
    return object
