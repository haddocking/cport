from urllib import request
import numpy as np
import os
from IPython import embed

class SeqFile:

    def __init__(self, string, name,main_dir,seq_dir):
        self.as_string = string
        self.name = name
        self.seq_dir = seq_dir
        self.format = os.path.basename(seq_dir).split(".")[-1]

def save_seq_to_temp_dir(main_dir,seq_string,name,format):
    temp_dir = os.path.join(main_dir, "temp")
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    seq_file = "{}.{}".format(name, format)

    seq_dir = os.path.join(temp_dir,seq_file)
    if not os.path.exists(seq_dir):
        save_file = open(seq_dir, "w")
        save_file.write(seq_string)
        save_file.close()
    return seq_dir

def from_file(seq_dir, name, main_dir,format):
    seq_string = open(seq_dir, "rb").read().decode("UTF-8")
    seq_dir = save_seq_to_temp_dir(main_dir,seq_string,name,format)
    seq_object = SeqFile(seq_string,name,main_dir,seq_dir)
    return seq_object


def from_url(seq_url, name, main_dir,format):
    seq_string = request.urlopen(seq_url).read().decode("utf-8")
    seq_dir = save_seq_to_temp_dir(main_dir,seq_string,name,format)
    seq_object = SeqFile(seq_string,name,main_dir,seq_dir)
    return seq_object

def fetch_from_id(pdb_id,format,main_dir):
    seq_url = "https://www.rcsb.org/fasta/entry/{}/display".format(pdb_id)
    object = from_url(seq_url,pdb_id,main_dir,format)
    return object
