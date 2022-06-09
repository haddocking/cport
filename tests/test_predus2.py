# Test if the predus2 prediction is working
from pathlib import Path

import pytest

from cport.modules.predus2 import Predus2


@pytest.fixture
def precalc_result():
    return Path(Path(__file__).parents[1], "tests/test_data/predus2_result.txt")


@pytest.fixture
def predus2():
    yield Predus2("tests/test_data/1PPE.pdb", "E")


@pytest.mark.skip("Cannot guarantee that the PredUs2 server is up")
def test_submit():
    pass


def test_retrieve_prediction_link(predus2):
    page_text = "PredUs2.0 result file:"
    observed_download_url = predus2.retrieve_prediction_link(page_text=page_text)
    expected_download_url = "https://honiglab.c2b2.columbia.edu/hfpd/tmp/1ppe_E.pd2.txt"
    assert observed_download_url == expected_download_url


@pytest.mark.skip("Cannot test the download")
def test_download_results():
    pass


def test_parse_prediction(predus2, precalc_result):
    observed_result_dic = predus2.parse_prediction(test_file=precalc_result)

    assert "active" in observed_result_dic
    assert "passive" in observed_result_dic

    assert len(observed_result_dic["active"]) == 26
    assert len(observed_result_dic["passive"]) == 193


@pytest.mark.skip("Overlaps with previous")
def test_run():
    pass
