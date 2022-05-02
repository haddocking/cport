import os
from urllib import request


class PdbFile:
    def __init__(self, string, name, pdb_dir):
        self.as_string = string
        self.name = name
        self.pdb_dir = pdb_dir
        self.pdb_id = None

    def save_file(self, pdb_dir):
        if not pdb_dir.startswith("./") and not pdb_dir.startswith("/"):
            pdb_dir = "./" + pdb_dir

        if not pdb_dir.endswith(".pdb"):
            pdb_dir = pdb_dir + ".pdb"

        folder_name = os.path.dirname(pdb_dir)
        full_dir = os.path.abspath(pdb_dir)
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        text_file = open(full_dir, "w")
        text_file.write(self.as_string)
        text_file.close()
        self.pdb_dir = full_dir

    def get_chain_ids(self):
        chains = []
        for line in self.as_string.split(os.linesep):
            if line.startswith("ATOM"):
                chain = line[20:23]
                chains.append(chain.strip())
        return list(set(chains))

    """
    I extract the scores from the b-factor column
    returns a list of tubules with residue number and the score (b-factor)
    the list is sorted from the larger to smaller score
    """

    def return_res_number_score(self):
        res_score = []
        for line in self.as_string.split(os.linesep):
            if line.startswith("ATOM"):
                number = int(line[23:26].strip())
                b_factor = float(line[61:66].strip())
                res_score.append((number, b_factor))
        res_score = set(res_score)
        res_score = sorted(res_score, key=lambda x: x[1], reverse=True)
        return res_score


"""
The pdb object can only get a string as input
Using the functions below I can convert 3 different PDB inputs to string
main_dir is the directory of the run
Each time I create a pdb object, it saves the PDB as file to the temp directory
"""


def clear_pdb_string(pdb_string, chain=None):
    final_string = ""
    if chain is None:
        for line in pdb_string.split(os.linesep):
            if (
                line.startswith("ATOM")
                or line.startswith("TER")
                or line.startswith("END")
            ):
                final_string += f"{line}" + os.linesep
    else:
        for line in pdb_string.split(os.linesep):
            if line.startswith("ATOM") or line.startswith("TER"):
                chain_in_line = line[21]
                if chain is not chain_in_line:
                    continue
                final_string += f"{line}" + os.linesep
            if line.startswith("END"):
                final_string += f"{line}" + os.linesep
    return final_string


def save_pdb_to_temp_dir(main_dir, pdb_string, name):
    temp_dir = os.path.join(main_dir, "temp")
    string_temp_dir = os.path.join(os.path.basename(main_dir), "temp")
    print(f"PDB {name} is saved to the temp folder {string_temp_dir}" + os.linesep)
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    pdb_file = "{}.pdb".format(name)
    pdb_dir = os.path.join(temp_dir, pdb_file)

    if not os.path.exists(pdb_dir):
        save_file = open(pdb_dir, "w")
        save_file.write(pdb_string)
        save_file.close()

    return pdb_dir


def from_file(pdb_dir, name, main_dir, chain=None):
    pdb_string = open(pdb_dir, "rb").read().decode("UTF-8")
    clean_pdb_string = clear_pdb_string(pdb_string, chain)
    pdb_dir = save_pdb_to_temp_dir(main_dir, clean_pdb_string, name)
    pdb_object = PdbFile(clean_pdb_string, name=name, pdb_dir=pdb_dir)
    return pdb_object


def from_url(pdb_url, name, main_dir, chain=None):
    pdb_string = request.urlopen(pdb_url).read().decode("utf-8")
    clean_pdb_string = clear_pdb_string(pdb_string, chain)
    pdb_dir = save_pdb_to_temp_dir(main_dir, clean_pdb_string, name)
    pdb_object = PdbFile(clean_pdb_string, name=name, pdb_dir=pdb_dir)
    return pdb_object


def from_string(pdb_string, name, main_dir, chain=None):
    pdb_string = clear_pdb_string(pdb_string, chain)
    pdb_dir = save_pdb_to_temp_dir(main_dir, pdb_string, name)
    pdb_object = PdbFile(pdb_string, name=name, pdb_dir=pdb_dir)
    return pdb_object


def fetch_from_id(pdb_id, main_dir, chain=None):
    name = pdb_id
    pdb_url = "http://files.rcsb.org/view/{}.pdb".format(name)
    pdb_object = from_url(pdb_url, name, main_dir, chain)
    return pdb_object
