from os.path import exists

import pandas as pd


def parse_arctic3d_output(filename):

    """
    Parse the .out file to obtain the ARCTIC3D active residues of the protein

    Parameters
    ------
    filename:
        The .out file that contains the active residues detected by ARCTIC3D for the specific PDB ID of a receptor


    Output
    ------
    uniqueResidues:
        A list that contains the unique active residues for the specific PDB ID


    """

    file = open(filename, "r")
    residues = ""
    for line in file:
        pos = line.find(">")
        s = line[pos + 1 :]
        residues += s
    residues = residues.replace("\n", " ")
    residues = residues.split(" ")

    # print(residues)

    uniqueResidues = []
    for x in residues:
        if x != "" and x not in uniqueResidues:
            uniqueResidues.append(int(x))

    uniqueResidues = sorted(uniqueResidues)
    # print(uniqueResidues)

    return uniqueResidues


def read_csv_to_pd(filename):

    df = pd.read_csv(filename, encoding="utf-8-sig")
    # print(df.columns)

    return df


def add_row_to_preds(df, active_list):

    """
    Adds the row that contains ARCTIC3D binary data to the dataframe that contains the predictors

    Parameters
    ------
    df:
        dataframe that contains the predictors as rows and their corresponding values for each residue
    active_list:
        list of active residues of the protein

    Outputs
    ------
    new_df:
        predictions dataframe that includes the ARCTIC3D active residues as a row

    """

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


def write_into_file(df, protein_name):

    path = (
        "/Users/erdemkertmen/Desktop/cport-2.0-documentation/training_dataset_w_values"
    )
    path = path + "/" + protein_name + "_cport_ready.csv"
    df.to_csv(path)
    return


# 1IRAtrunc and 2OT3 arctic3d output not found

pdbs = [
    "2A9K",
    "1RV6",
    "3L89",
    "1JMO",
    "3PC8",
    "4FZA",
    "1M10",
    "2SNI",
    "3S9D",
    "2FJU",
    "1EXB",
    "3SZK",
    "1KTZ",
    "1T6B",
    "1I4D",
    "1GRN",
    "1Z5Y",
    "2O3B",
    "1ATN",
    "3H11",
    "2HLE",
    "1XU1",
    "3AAD",
    "1M27",
    "2A5T",
    "1IRA",
    "1MQ8",
    "3BX7",
    "1A2K",
    "1KXP",
    "1JZD",
    "2HQS",
    "1D6R",
    "1ZHH",
    "2GAF",
    "3CPH",
    "1F6M",
    "1EER",
    "2H7V",
    "1KLU",
    "1TMQ",
    "2B42",
    "1CLV",
    "2UUY",
    "1RKE",
    "1ZHI",
    "1ACB",
    "1ZM4",
    "1EFN",
    "1B6C",
    "2B4J",
    "1S1Q",
    "1OFU",
    "3K75",
    "1YVB",
    "1GHQ",
    "2AJF",
    "2VDB",
    "1ZLI",
    "2NZ8",
    "1FQJ",
    "3R9A",
    "1CGI",
    "2OOB",
    "2CFH",
    "1RLB",
    "1JTD",
    "3P57",
    "2J0T",
    "3FN1",
    "1Y64",
    "1H1V",
    "1DE4",
    "2A1A",
    "1GP2",
    "1GPW",
    "4HX3",
    "2X9A",
    "1XQS",
    "1HE1",
    "1PXV",
    "1WDW",
    "1HE8",
    "1K5D",
    "1FC2",
    "1OPH",
    "4GAM",
    "2MTA",
    "1AZS",
    "1AVX",
    "1E6E",
    "7CEI",
    "1FCC",
    "1AY7",
    "1UDI",
    "1EZU",
    "1E96",
    "2G77",
    "1DFJ",
    "1R8S",
    "2Z0E",
    "2OUL",
    "1BKD",
    "1FAK",
    "3F1P",
    "1I2M",
    "1PVH",
    "1R0R",
    "1K74",
    "2OZA",
    "2AYO",
    "3AAA",
    "9QFW",
    "1EWY",
    "4H03",
    "2I9B",
    "1JK9",
    "1GXD",
    "BP57",
    "2C0L",
    "1PPE",
    "1Z0K",
    "3VLB",
    "1R6Q",
    "3H2V",
    "1GLA",
    "1IJK",
    "1F34",
    "CP57",
    "2ABZ",
    "1XD3",
    "2PCC",
    "3SGQ",
    "3BIW",
    "1F51",
    "1GL1",
    "4M76",
    "2BTF",
    "2IDO",
    "2J7P",
    "2HRK",
    "2YVJ",
    "1BUH",
    "1ML0",
    "1GCQ",
    "1H9D",
    "1BVN",
    "1OC0",
    "1WQ1",
    "2OOR",
    "1KAC",
    "1AK4",
    "1EAW",
    "1US7",
    "1J2J",
    "4IZ7",
    "1MAH",
    "1IB1",
    "4JCV",
    "1AKJ",
    "1NW9",
    "1SYX",
    "1JWH",
    "1JTG",
    "1N2C",
    "3DAW",
    "1IBR",
    "3A4S",
    "BAAD",
    "4CPA",
    "1KKL",
    "1FQ1",
    "2SIC",
    "1OYV",
    "3BP8",
    "1QA9",
    "3LVK",
    "1SBB",
    "1FFW",
    "1FLE",
    "3D5S",
    "1JIW",
    "2GTP",
    "4LW4",
    "1LFD",
    "1HCF",
    "2O8V",
    "1HIA",
    "BOYV",
]

print(len(pdbs))

first_iteration = True

for pdbID in pdbs:

    if (
        exists(f"/Users/erdemkertmen/cport/output/predictors_{pdbID}_r_uw_values.csv")
        == False
    ):
        continue

    active_residues = parse_arctic3d_output(
        f"/Users/erdemkertmen/Desktop/cport_analysis-documentation/output/arctic3d_output/{pdbID}/clustered_residues.out"
    )
    df = read_csv_to_pd(
        f"/Users/erdemkertmen/cport/output/predictors_{pdbID}_r_uw_values.csv"
    )

    df = add_row_to_preds(df, active_residues)

    df = df.transpose()
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)

    # print(df.columns)

    if first_iteration:
        main_df = df
        first_iteration = False

    else:
        main_df = pd.concat([main_df, df], axis=0)

    # print(df)

    write_into_file(df, pdbID)

# main_df.drop(['cons_ppisp', 'predictprotein', 'Whiscy'], axis=1, inplace=True)

main_df.replace("P", 0.0, inplace=True)
main_df.replace("-", 0.0, inplace=True)
main_df.replace("A", 1.0, inplace=True)
main_df.replace("AP", 0.5, inplace=True)

main_df = main_df.astype(float)
main_df.reset_index(inplace=True, drop=True)

print(main_df.shape)

output_file = "/Users/erdemkertmen/Desktop/cport-2.0-documentation/training_dataset_w_values/master.csv"
main_df.to_csv(output_file)
