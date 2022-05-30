# Test if the Predict Protein prediction is working
from pathlib import Path

import pytest

from cport.modules.predictprotein_api import Predictprotein


@pytest.fixture
def precalc_result():
    return Path(Path(__file__).parents[1], "tests/test_data/predictprotein_result.txt")


@pytest.fixture
def predictprotein():
    yield Predictprotein("1ppe", "E")


@pytest.mark.skip("Cannot guarantee that the Predict Protein server is up")
def test_submit():
    pass


def test_parse_prediction(predictprotein, precalc_result):
    observed_result_dic = predictprotein.parse_prediction(test_file=precalc_result)

    assert "active" in observed_result_dic
    assert "passive" in observed_result_dic

    assert 0 not in observed_result_dic["active"]
    assert 0 not in observed_result_dic["passive"]

    assert len(observed_result_dic["active"]) == 29
    assert len(observed_result_dic["passive"]) == 194


@pytest.mark.skip("Overlaps with previous")
def test_run():
    pass
