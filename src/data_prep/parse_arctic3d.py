import glob
import json

import numpy as np

np.set_printoptions(threshold=np.inf)


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


"""
all_pdbs = glob.glob("/Users/erdemkertmen/BM5-clean/HADDOCK-ready/*")
pdbs = []
for x in range(0, len(all_pdbs)):
    all_pdbs[x] = all_pdbs[x].split("/")[5]
    if len(all_pdbs[x]) == 4 and all_pdbs[x] != "data":
        pdbs.append(all_pdbs[x])
    elif all_pdbs[x] == "1IRAtrunc":
        pdbs.append(all_pdbs[x])
#print(all_pdbs)
print(pdbs)
print(len(pdbs))
"""

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
    "1IRAtrunc",
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
    "2OT3",
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

# print(len(pdbs))

pdb_and_uniprot = {}

files = glob.glob(
    "/Users/erdemkertmen/Downloads/bm5_dataset_execution/arctic3d-*/arctic3d.log"
)


empty_files = []
supplementary_pdbIDs = []
missing_pdbIDs = [
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
    "1IRAtrunc",
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
    "2OT3",
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

cnt = 0
for filename in files:

    dic = read_log(filename)

    # print(dic)

    if dic != "Empty dict":
        cnt += 1
        for key in dic:
            a = key.split("-")
            uniprotID = a[0]
            pdbID = a[1].upper()
            chainID = a[2]
            if pdbID in pdbs:

                if pdbID in pdb_and_uniprot:
                    if uniprotID not in pdb_and_uniprot[pdbID].keys():
                        pdb_and_uniprot[str(pdbID)][uniprotID] = [chainID]
                    else:
                        if chainID not in pdb_and_uniprot[str(pdbID)][uniprotID]:
                            pdb_and_uniprot[str(pdbID)][uniprotID].append(chainID)
                else:
                    pdb_and_uniprot[str(pdbID)] = {uniprotID: [chainID]}

                if pdbID in missing_pdbIDs:
                    missing_pdbIDs.remove(pdbID)

            elif pdbID not in supplementary_pdbIDs:
                supplementary_pdbIDs.append(pdbID)

    else:
        empty_files.append(filename)
# print(cnt)

# print(pdb_and_uniprot)
count = 0
print(pdb_and_uniprot)
for key, value in pdb_and_uniprot.items():
    print(key, ":", pdb_and_uniprot[key])
    count += 1
print("\n", count, "pdbIDs are present from BM5")
print(list(pdb_and_uniprot.keys()))

print("\n", "List of empty files:", empty_files)
print("\n", "Missing pdbIDs from BM5:", missing_pdbIDs)
print("\n", len(missing_pdbIDs), "of the pdbIDs from BM5 are missing")
# print("\n","Supplementary pdbIDs that are not in BM5:", np.unique(np.array(supplementary_pdbIDs)))
