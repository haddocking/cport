# Test if the Predict Protein prediction is working
from pathlib import Path

import pytest

from cport.modules.predictprotein import Predictprotein
from cport.url import PREDICTPROTEIN_URL


@pytest.fixture
def precalc_result():
    return Path(Path(__file__).parents[1], "tests/test_data/predictprotein_result.txt")


@pytest.fixture
def predictprotein():
    yield Predictprotein("1ppe", "E")


@pytest.mark.skip("Cannot guarantee that the Predict Protein server is up")
def test_submit():
    pass


@pytest.mark.skip("Cannot test the download")
def test_retrieve_prediction_file(predictprotein):
    pass


def test_parse_prediction(predictprotein, precalc_result):
    observed_result_dic = predictprotein.parse_prediction(test_file=precalc_result)

    assert "active" in observed_result_dic
    assert "passive" in observed_result_dic

    assert len(observed_result_dic["active"]) == 29
    assert len(observed_result_dic["passive"]) == 194


@pytest.mark.skip("Overlaps with previous")
def test_run():
    pass
