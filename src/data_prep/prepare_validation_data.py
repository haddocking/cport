import glob
import json
import os

import numpy as np
import pandas as pd


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

    """
    Reads the log files of the ARCTIC3D output files to parse the interface residues detected by ARCTIC3D

    Parameters
    ------
    filename:
        name of the .log file

    Outputs
    ------
    dict:
        dictionary of interface residues

    """

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


def write_into_file(df, protein_name):
    path = "../../data/ligand_PDBs/validation_dataset_w_values"
    path = path + "/" + protein_name + "_cport_ready.csv"
    df.to_csv(path)
    return


def add_row_to_preds(df, active_list):

    firstCol = df.columns[1]
    lastCol = df.columns[-1]

    # print(firstCol)
    # print(lastCol)

    new_row = {}
    new_row["predictor"] = "arctic3d_interaction"
    for i in range(int(firstCol), int(lastCol) + 1):
        if i in active_list:
            new_row[str(i)] = 1
        else:
            new_row[str(i)] = 0
    # print(new_row)

    new_df = df._append(new_row, ignore_index=True)

    # print(new_df)
    return new_df


acc_codes = get_acc_codes(
    "/Users/erdemkertmen/Desktop/cport-2.0-documentation/ligand parsed.txt"
)
acc_codes = list(acc_codes)

acc_codes.remove("P41832")
acc_codes.remove("P01074")
acc_codes.remove("Q1PIV4")

# print(acc_codes)

active_residues = {}

print(acc_codes)

files = glob.glob(
    "/Users/erdemkertmen/Downloads/bm5_dataset_execution/arctic3d-*/arctic3d.log"
)
for filename in files:
    uniprot_name = filename.split("/")[5][9:]
    # print(uniprot_name)
    dic = read_log(filename)

    # print(dic)

    if dic != "Empty dict":
        for key in dic:
            a = key.split("-")
            uniprotID = a[0].upper()
            pdbID = a[1].upper()
            chainID = a[2]
            if uniprot_name in acc_codes:

                if uniprot_name not in active_residues.keys():
                    active_residues[uniprot_name] = list(dic[key])
                else:
                    active_residues[uniprot_name] += list(dic[key])

            if uniprotID in acc_codes:
                if uniprotID not in active_residues.keys():
                    active_residues[uniprotID] = list(dic[key])
                else:
                    active_residues[uniprotID] += list(dic[key])


for key in active_residues.keys():
    active_residues[key] = sorted(set(active_residues[key]))

"""print(active_residues["P62993"])
print(len(active_residues["P62993"]))


print(len(active_residues.keys()))
"""
print(active_residues)

files = glob.glob("../../data/ligand_PDBs/output/predictors_*w_values.csv")

for fname in files:

    # fname = "/Users/erdemkertmen/Desktop/ligand_PDBs/output/cport_P62993.csv"
    acc_code = fname.split("/")
    acc_code = acc_code[6][11:17]

    # print(active_residues[acc_code])

    df = pd.read_csv(fname)

    # print(len(df.columns))

    arctic3d_data = []
    for i in range(1, len(df.columns) + 1):
        if i in list(active_residues[acc_code]):
            arctic3d_data.append(1)
        else:
            arctic3d_data.append(0)

    # print(arctic3d_data)

    df = add_row_to_preds(df, active_residues[acc_code])

    df = df.transpose()
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)

    write_into_file(df, acc_code)


"""tp = 0
tn = 0
fp = 0
fn = 0

for i in df.index:
    if df["arctic3d_data"][i] == 1 and df["threshold_pred"][i] == 1:
        tp += 1
    elif df["arctic3d_data"][i] == 0 and df["threshold_pred"][i] == 1:
        fp += 1
    elif df["arctic3d_data"][i] == 1 and df["threshold_pred"][i] == 0:
        fn += 1
    else:
        tn += 1

sensitivity = tp / (tp + fn)
precision = tp / (tp + fp)

print("True Positive", tp)
print("True Negative", tn)
print("False Positive", fp)
print("False Negative", fn)

print("Sensitivity", sensitivity)
print("Precision", precision)"""
