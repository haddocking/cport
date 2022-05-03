# Test if the pdb_fasta function is working
import os
from cport.modules.utils import get_fasta_from_pdbid


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
