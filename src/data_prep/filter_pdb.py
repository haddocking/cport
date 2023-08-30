import glob

import pandas as pd


def extract_pdb_dt(path: str) -> dict:
    pdb_chains = {}
    # Read file
    with open(path, "r") as f:
        # Loop over lines
        for _ in f:
            # Skip non ATOM / HETATM lines
            if not any(
                [
                    _.startswith("ATOM"),
                    # _.startswith('HETATM'),
                ]
            ):
                continue

            # Extract residue name
            resname = _[17:20]
            # Extract chain id
            chainid = _[21:22]
            # Extract resid
            resid = _[22:26]
            # B-factor
            bfactor = _[60:66]
            # Check if chain already parsed
            if not chainid in pdb_chains.keys():
                # Initiate new chain holder
                pdb_chains[chainid] = {"order": []}
            # Check if new resid id
            if not resid in pdb_chains[chainid].keys():
                # Add to oredered resids
                pdb_chains[chainid]["order"].append(resid)
                # Initiate new residue holder
                pdb_chains[chainid][resid] = {
                    "resname": resname,
                    "chainid": chainid,
                    "atoms": [],
                    "resid": resid,
                    "bfactor": bfactor,
                }
            # Add atom line
            pdb_chains[chainid][resid]["atoms"].append(_)
    return pdb_chains


def filter_bfactor(pdbchain: dict, bfactor_threshold: float = 80.0):
    filtered_in, filtered_out = [], []
    for resindex in pdbchain["order"]:
        residue = pdbchain[resindex]
        if float(residue["bfactor"]) >= bfactor_threshold:
            filtered_in.append(residue["resid"])
        else:
            filtered_out.append(residue["resid"])
    return filtered_in, filtered_out


csv_files = glob.glob(
    "../../data/ligand_PDBs/validation_dataset_w_values/*_cport_ready.csv"
)

first_iteration = True

for file in csv_files:

    acc_code = file.split("/")[6][:6]

    pdb_chains = extract_pdb_dt(f"../../data/ligand_PDBs/{acc_code}.pdb")
    filtered_in, filtered_out = filter_bfactor(pdb_chains["A"])

    above_treshold = []

    for res in filtered_in:
        res = res.strip()
        res = int(res)
        # print(res)
        above_treshold.append(res)

    # print(above_treshold)

    # file_to_read = "/Users/erdemkertmen/Desktop/ligand_PDBs/validation_dataset_w_values/Q07889_cport_ready.csv"

    df = pd.read_csv(file)

    above_df = pd.DataFrame()
    below_df = pd.DataFrame()

    for index, row in df.iterrows():
        if (index + 1) in above_treshold:
            above_df = above_df._append(row)

        else:
            below_df = below_df._append(row)

    above_df.to_csv(
        f"../../data/ligand_PDBs/validation_dataset_w_values/above_treshold/{acc_code}.csv"
    )
    below_df.to_csv(
        f"../../data/ligand_PDBs/validation_dataset_w_values/below_treshold/{acc_code}.csv"
    )

    # above_df.columns = above_df.iloc[0]
    # above_df.reset_index(inplace=True, drop=True)
    # above_df.drop(above_df.index[0], inplace=True)

    # below_df.columns = below_df.iloc[0]
    # below_df.reset_index(inplace=True, drop=True)
    # below_df.drop(below_df.index[0], inplace=True)

    # print(df.columns)

    if first_iteration:
        main_above_df = above_df
        main_below_df = below_df
        first_iteration = False

    else:
        main_above_df = pd.concat([main_above_df, above_df], axis=0, ignore_index=True)
        main_below_df = pd.concat([main_below_df, below_df], axis=0, ignore_index=True)

main_above_df.drop(labels="Unnamed: 0", axis="columns", inplace=True)
main_above_df.replace("P", 0.0, inplace=True)
main_above_df.replace("-", 0.0, inplace=True)
main_above_df.replace("A", 1.0, inplace=True)
main_above_df.replace("AP", 0.5, inplace=True)

main_above_df = main_above_df.astype(float)

main_below_df.drop(labels="Unnamed: 0", axis="columns", inplace=True)
main_below_df.replace("P", 0.0, inplace=True)
main_below_df.replace("-", 0.0, inplace=True)
main_below_df.replace("A", 1.0, inplace=True)
main_below_df.replace("AP", 0.5, inplace=True)

main_below_df = main_below_df.astype(float)

main_above_df.to_csv(
    f"../../data/ligand_PDBs/validation_dataset_w_values/above_treshold/above_master.csv"
)
main_below_df.to_csv(
    f"../../data/ligand_PDBs/validation_dataset_w_values/below_treshold/below_master.csv"
)


# print(above_df)
