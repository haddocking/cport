from IPython import embed
from urllib import request
import numpy as np
import os


class PdbFile:

    def __init__(self, string, name,main_dir,pdb_dir=None):
        self.as_string = string
        self.name = name
        self.main_dir = main_dir
        self.save_to_temp()

    def save_to_temp(self):
        temp_dir = os.path.join(self.main_dir,"temp")
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        pdb_temp = os.path.join(temp_dir, "{}.pdb".format(self.name))
        self.save_file(pdb_temp)
        self.pdb_dir = pdb_temp

    def save_file(self, pdb_dir):
        if not pdb_dir.startswith("./") and not pdb_dir.startswith("/"):
            pdb_dir = "./" + pdb_dir
        if not pdb_dir.endswith(".pdb"):
            pdb_dir = pdb_dir+".pdb"
        folder_name = os.path.dirname(pdb_dir)
        full_dir = os.path.abspath(pdb_dir)
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        text_file = open(full_dir, "w")
        text_file.write(self.as_string)
        text_file.close()
        self.pdb_dir = full_dir

    def get_larger_chain(self):
        chains = []
        for line in self.as_string.split("\n"):
            if line.startswith("ATOM"):
                chain = line[20:23]
                chains.append(chain.strip())
        chain_names, chain_counts = np.unique(chains, return_counts=True)
        idx = chain_counts == max(chain_counts)
        return chain_names[idx].tolist()[0]

    """
    I extract the scores from the b-factor column
    returns a list of tubules with residue number and the score (b-factor)
    the list is sorted from the larger to smaller score
    """
    def return_res_number_score(self):
        res_score = []
        for line in self.as_string.split("\n"):
            if line.startswith("ATOM"):
                number = int(line[23:26].strip())
                b_factor = float(line[60:77].strip())
                res_score.append((number, b_factor))
        res_score = set(res_score)
        res_score = sorted(res_score, key=lambda x: x[1], reverse=True)
        return res_score


"""
The pdb object can only get a string as input. 
Using the functions below I can convert 3 different PDB inputs to string 
Then I can create the Object
main_dir is the directory of the run
Each time I create a pdb object, it saves the PDB as file to the temp directory
"""

def from_file(pdb_dir, name,main_dir):
    pfile = PdbFile(open(pdb_dir, 'r').read(), name=name,main_dir=main_dir)
    return pfile


def from_url(pdb_url, name,main_dir):
    pfile = PdbFile(request.urlopen(pdb_url).read().decode("utf-8"), name=name,main_dir=main_dir)
    return pfile


def from_string(pdb_string, name,main_dir):
    pfile = PdbFile(pdb_string, name,main_dir)
    return pfile
