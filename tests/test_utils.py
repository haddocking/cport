"""Test the utility functions."""
import filecmp
import os
import tempfile
from pathlib import Path

import pytest

from cport.modules.utils import (
    format_output,
    get_fasta_from_pdbid,
    get_pdb_from_pdbid,
    get_residue_range,
)


@pytest.fixture
def test_result_dic():
    return {
        "something": {"passive": [1, 5], "active": [2, 6]},
        "somethingelse": {"passive": [5, 7], "active": [3, 2]},
    }


def test_get_fasta_from_pdbid():
    """Test the execution of the pdb_fasta function."""
    observed_fasta = get_fasta_from_pdbid("1PPE", "E")
    expected_fasta = (
        ">1PPE_1|Chain A[auth E]|TRYPSIN|Bos taurus (9913)"
        f"{os.linesep}IVGGYTCGANTVPYQVSLNSGYHFCGGSLINSQWVVS"
        "AAHCYKSGIQVRLGEDNINVVEGNEQFISASKSIVHPSYNSNTLNNDIML"
        "IKLKSAASLNSRVASISLPTSCASAGTQCLISGWGNTKSSGTSYPDVLKC"
        "LKAPILSDSSCKSAYPGQITSNMFCAGYLEGGKDSCQGDSGGPVVCSGKL"
        "QGIVSWGSGCAQKNKPGVYTKVCNYVSWIKQTIASN"
    )

    assert observed_fasta == expected_fasta


def test_get_pdb_from_pdbid():
    """Test the PDB retrieval via the get_pdb function"""
    observed_pdb = get_pdb_from_pdbid("1PPE")
    expected_pdb = Path(Path(__file__).parents[1], "tests/test_data/1PPE.pdb")
    assert filecmp.cmp(observed_pdb, expected_pdb)


def test_format_output(test_result_dic, pdb_file = "tests/test_data/1PPE.pdb", chain_id = "E"):

    output_f = Path(tempfile.NamedTemporaryFile(delete=False, mode="w+").name)
    format_output(test_result_dic, output_f, pdb_file, chain_id)

    expected_output_f = Path(
        Path(__file__).parents[1], "tests/test_data/test_output.csv"
    )

    assert filecmp.cmp(output_f, expected_output_f)

    os.unlink(output_f)


def test_get_residue_range(test_result_dic):

    observed_residue_list = get_residue_range(test_result_dic)
    expected_residue_lsit = [1, 2, 3, 4, 5, 6]

    assert isinstance(observed_residue_list, list)
    assert observed_residue_list == expected_residue_lsit
