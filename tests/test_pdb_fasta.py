# Test if the pdb_fasta function is working
from cport.modules.tools import pdb_fasta

import pytest


@pytest.fixture
def pdb_to_fasta():
    yield pdb_fasta.get_pdb_fasta("1PPE", "E")


def test_run_pdb_fasta(pdb_to_fasta):
    """Test the execution of the pdb_fasta function."""
    observed_predictions = pdb_to_fasta
    expected_predictions = ">1PPE_1|Chain A[auth E]|TRYPSIN|Bos taurus (9913)\nIVGGYTCGANTVPYQVSLNSGYHFCGGSLINSQWVVSAAHCYKSGIQVRLGEDNINVVEGNEQFISASKSIVHPSYNSNTLNNDIMLIKLKSAASLNSRVASISLPTSCASAGTQCLISGWGNTKSSGTSYPDVLKCLKAPILSDSSCKSAYPGQITSNMFCAGYLEGGKDSCQGDSGGPVVCSGKLQGIVSWGSGCAQKNKPGVYTKVCNYVSWIKQTIASN"

    assert observed_predictions == expected_predictions
