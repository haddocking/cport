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

from cport.url import PDB_FASTA_URL, PDB_URL

log = logging.getLogger("cportlog")


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


def format_output(result_dic, output_fname):
    """
    Format the results into a human-readable format.

    Parameters
    ----------
    result_dic : dict
        The results dictionary.
    output_fname : str or pathlib.PosixPath
        The output file name.

    """
    reslist = get_residue_range(result_dic)
    data = []
    for pred in result_dic:
        row = [pred]
        if pred != "whiscy" or "sppider":
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
    active_reslist = list(
        itertools.chain(*[result_dic[e]["active"] for e in result_dic])
    )
    # workaround to compensate for tuples in the active_reslist
    reslist = passive_reslist + [x[0] for x in active_reslist]
    absolute_range = list(range(min(reslist), max(reslist)))
    return absolute_range
