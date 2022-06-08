# Test if the CSM-Potential prediction is working
from pathlib import Path

import pytest

from cport.modules.csm_potential import CsmPotential


@pytest.fixture
def precalc_result():
    return Path(Path(__file__).parents[1], "tests/test_data/csm_potential_result.txt")


@pytest.fixture
def csm_potential():
    yield CsmPotential("1ppe", "E")


@pytest.mark.skip("Cannot guarantee that the CSM-Potential server is up")
def test_submit():
    pass


def test_parse_prediction(csm_potential, precalc_result):
    observed_result_dic = csm_potential.parse_prediction(test_file=precalc_result)

    assert "active" in observed_result_dic
    assert "passive" in observed_result_dic

    assert 0 not in observed_result_dic["active"]
    assert 0 not in observed_result_dic["passive"]

    assert len(observed_result_dic["active"]) == 69
    assert len(observed_result_dic["passive"]) == 151


@pytest.mark.skip("Overlaps with previous")
def test_run():
    pass
