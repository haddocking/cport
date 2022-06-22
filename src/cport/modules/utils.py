"""Utilities for CPORT."""
import itertools
import logging
import os
import re
import sys
import tempfile
from urllib import request

import pandas as pd
import requests
from Bio import SeqIO

from cport.url import PDB_FASTA_URL, PDB_URL

log = logging.getLogger("cportlog")

scored_predictors = [
    "cons_ppisp",
    "meta_ppisp",
    "ispred4",
    "predictprotein",
    "predus2",
    "psiver",
    "scriber",
    "csm_potential",
]

pdb_predictors = [
    "whiscy",
    "ispred4",
    "meta_ppisp",
    "cons_ppisp",
    "predus2",
    "sppider",
    "csm_potential",
]


def get_fasta_from_pdbid(pdb_id, chain_id):
    """
    Retrieve the Fasta string file given a PDBid/Chain.

    Parameters
    ----------
    pdb_id : str
        Protein data bank identification code.
    chain_id : str
        Chain identifier.

    Returns
    -------
    fasta_seq : str
        Fasta sequence.

    """
    # https://regex101.com/r/qjjIih/1
    # https://regex101.com/r/lVRUIQ/1
    chain_regex = r"Chain\s(\S)|Chains\s(\S)|auth\s(\S)"

    target_url = f"{PDB_FASTA_URL}{pdb_id}#{chain_id}/download"
    fasta_seqs = requests.get(target_url).text

    seq_dic = {}
    for line in fasta_seqs.split(os.linesep):
        if not line:
            continue
        if line.startswith(">"):
            # -1-1 will prioritize the AUTH chain ID
            chain = re.findall(chain_regex, line)[-1][-1]
            seq_dic[chain] = line + os.linesep
        else:
            seq_dic[chain] += line

    fasta_seq = seq_dic[chain_id]

    if chain_id not in seq_dic:
        log.error("Could not find chain %s in %s", chain_id, pdb_id)
        sys.exit()
    else:
        return fasta_seq


def get_pdb_from_pdbid(pdb_id):
    """
    Retrieve the PDB file from a given PDBid.

    Parameters
    ----------
    pdb_id : str
        Protein data bank identification code.

    Returns
    -------
    pdb_fname : str
        A temporary file containing the PDB.

    """
    target_url = f"{PDB_URL}{pdb_id}.pdb"
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    # trunk-ignore(bandit/B310)
    request.urlretrieve(target_url, temp_file.name)

    pdb_fname = temp_file.name

    return pdb_fname


def get_fasta_from_pdbfile(pdb_file, chain_id):
    """
    Extract FASTA sequence from supplied PDB file.

    Parameters
    ----------
    pdb_file : str
        Path to the supplied PDB file.
    chain_id : str
        Specific chain to return the FASTA string from.

    Returns
    -------
    sequence : str
        String of the FASTA sequence.

    """
    with open(pdb_file) as handle:
        for record in SeqIO.PdbIO.PdbSeqresIterator(handle):
            # checks all the chains to find match with chain_id
            if record.id[-1] == chain_id:
                sequence = str(record.seq)
    return sequence


def format_output(result_dic, output_fname, pdb_file, chain_id):
    """
    Format the results into a human-readable format.

    Parameters
    ----------
    result_dic : dict
        The results dictionary.
    output_fname : str or pathlib.PosixPath
        The output file name.

    """
    standardized_dic = standardize_residues(result_dic, chain_id, pdb_file)
    reslist = get_residue_range(standardized_dic)
    data = []
    for pred in result_dic:
        row = [pred]
        if pred in scored_predictors:
            active_list = [x[0] for x in result_dic[pred]["active"]]

            for res in reslist:
                is_passive = None
                is_active = None

                if res in result_dic[pred]["passive"]:
                    is_passive = True

                if res in active_list:
                    is_active = True
                    score = result_dic[pred]["active"][active_list.index(res)][1]

                if is_active and is_passive:
                    row.append("AP")
                elif is_active:
                    row.append(str(score))
                elif is_passive:
                    row.append("P")
                else:
                    row.append("-")
            # print(row)
            data.append(row)

        else:
            for res in reslist:
                is_passive = None
                is_active = None

                if res in result_dic[pred]["passive"]:
                    is_passive = True

                if res in result_dic[pred]["active"]:
                    is_active = True

                if is_active and is_passive:
                    row.append("AP")
                elif is_active:
                    row.append("A")
                elif is_passive:
                    row.append("P")
                else:
                    row.append("-")
            # print(row)
            data.append(row)

    output_df = pd.DataFrame(data, columns=["predictor"] + reslist)
    output_df.to_csv(output_fname, index=False)


def get_residue_range(result_dic):
    """
    Retrieve a range of residues considering a dictionary of predictions.

    Parameters
    ----------
    result_dic : dict
        The results dictionary.

    Returns
    -------
    absolute_range : list
        The list of residues.

    """
    passive_reslist = list(
        itertools.chain(*[result_dic[e]["passive"] for e in result_dic])
    )

    # due to the scored predictors using tuples, the extraction is different
    active_reslist = []
    for pred in result_dic:
        if pred in scored_predictors:
            active_reslist += [x[0] for x in result_dic[pred]["active"]]
        else:
            active_reslist += [x for x in result_dic[pred]["active"]]

    reslist = passive_reslist + active_reslist
    absolute_range = list(range(min(reslist), max(reslist)))
    return absolute_range


def standardize_residues(result_dic, chain_id, pdb_file):
    """
    Standardize the residues from different predictors
    into a uniform numbering system starting at 1.

    Parameters
    ----------
    result_dic: dict
        The results dictionary

    Returns
    -------
    result_dic : dict
        The standardized results dict

    """
    # https://regex101.com/r/jQFPmY/1
    bias_regex = r"\S"

    f = open(pdb_file, "r")
    pdb_text = "\n".join(f.read().splitlines())
    # pdb files start at a number residue, so remove this bias
    bias = int(re.findall(bias_regex, pdb_text)[10]) - 1

    # if there was no bias present, then no need to run through this block
    if bias != 0:
        for pred in result_dic:
            if pred not in scored_predictors and pred in pdb_predictors:
                for index in enumerate(result_dic[pred]["active"]):
                    result_dic[pred]["active"][index[0]] -= bias
                for index in enumerate(result_dic[pred]["passive"]):
                    result_dic[pred]["passive"][index[0]] -= bias
            elif pred in pdb_predictors:
                for index in enumerate(result_dic[pred]["active"]):
                    result_dic[pred]["active"][index[0]][0] -= bias
                for index in enumerate(result_dic[pred]["passive"]):
                    result_dic[pred]["passive"][index[0]] -= bias

    return result_dic
