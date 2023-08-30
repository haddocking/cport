import glob
import json
import os

import numpy as np


def get_uniprot(acc):

    """
    Downloads the pdb file of a UniProt protein by its accession code

    Parameters
    ------
    acc:
        UniProt accession code of a protein that the pdb file is desired to be downloaded



    """

    uniquery = f'curl "https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v4.pdb" >/Users/erdemkertmen/Desktop/ligand_PDBs/{acc}.pdb '

    os.system(uniquery)


def get_acc_codes(filename):

    """
    Parameters
    ------
    filename:
        file that contains the UniProt accession codes and corresponding PDB IDs of the ligands

    Outputs
    ------
    acc_codes:
        list of UniProt accession codes

    """

    f = open(filename, "r")
    acc_codes = []
    lines = f.readlines()
    for line in lines:
        id = line[5:].strip()
        if "-" not in id:
            acc_codes.append(id)
    # print(len(acc_codes))
    acc_codes = np.array(acc_codes)
    acc_codes = np.unique(acc_codes)
    # print(len(acc_codes))
    return acc_codes


def read_log(filename):
    s = ""

    with open(filename, "r") as f:
        for line in f:
            if "Interface Residues" in line:
                s = line

    if s == "":
        return "Empty dict"

    k = s.find(" Interface Residues")

    start = k + 20
    residues = s[start:].replace("'", '"')

    dict = json.loads(residues)

    return dict


acc_codes = get_acc_codes(
    "/Users/erdemkertmen/Desktop/cport-2.0-documentation/ligand parsed.txt"
)
acc_codes = list(acc_codes)

acc_codes.remove("P41832")
acc_codes.remove("P01074")
acc_codes.remove("Q1PIV4")

# print(acc_codes)

active_residues = {}


"""for acc in acc_codes:
    get_uniprot(acc)

    filename = f"/Users/erdemkertmen/Downloads/bm5_dataset_execution/arctic3d-{acc}/arctic3d.log"
"""

"""dic = read_log(filename)

    #print(dic)

    if dic != "Empty dict":
        for key in dic:
            a = key.split("-")
            uniprotID = a[0].upper()
            pdbID = a[1].upper()
            chainID = a[2]

            if uniprotID in acc_codes:
                if uniprotID not in active_residues.keys():
                    active_residues[uniprotID] = list(dic[key])
                else:
                    active_residues[uniprotID].append(list(dic[key]))"""

print(acc_codes)

files = glob.glob(
    "/Users/erdemkertmen/Downloads/bm5_dataset_execution/arctic3d-*/arctic3d.log"
)
for filename in files:

    dic = read_log(filename)

    # print(dic)

    if dic != "Empty dict":
        for key in dic:
            a = key.split("-")
            uniprotID = a[0].upper()
            pdbID = a[1].upper()
            chainID = a[2]
            if uniprotID in acc_codes:

                if uniprotID not in active_residues.keys():
                    active_residues[uniprotID] = list(dic[key])
                else:
                    active_residues[uniprotID] += list(dic[key])


for key in active_residues.keys():
    active_residues[key] = sorted(set(active_residues[key]))

print(active_residues)

print(len(active_residues.keys()))
