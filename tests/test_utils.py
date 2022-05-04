"""Test the utility functions."""
import os
import filecmp
from pathlib import Path
from cport.modules.utils import get_fasta_from_pdbid, get_pdb_from_pdbid


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
