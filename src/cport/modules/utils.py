import logging
import os
import re
import sys
import tempfile
from urllib import request

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
    chain_regex = r"Chain\s(\S)|auth\s(\S)"

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
        log.error(f"Could not find chain {chain_id} in {pdb_id}")
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
    request.urlretrieve(target_url, temp_file.name)

    pdb_fname = temp_file.name

    return pdb_fname
