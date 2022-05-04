# Test if the scriber prediction is working
from pathlib import Path

import pytest

from cport.modules.scriber import Scriber


@pytest.fixture
def precalc_result():
    return Path(Path(__file__).parents[1], "tests/test_data/scribber_result.csv")


@pytest.fixture
def scriber():
    yield Scriber("1PPE", "E")


@pytest.mark.skip("Cannot guarantee that the Scriber server is up")
def test_submit():
    pass


def test_retrieve_prediction_link(scriber):
    page_text = "http://thisisthetest.csv"
    observed_link = scriber.retrieve_prediction_link(page_text=page_text)
    expected_link = "http://thisisthetest.csv"
    assert observed_link == expected_link


@pytest.mark.skip("Cannot test the download")
def test_download_results():
    pass


def test_parse_prediction(scriber, precalc_result):
    observed_result_dic = scriber.parse_prediction(precalc_result)

    assert "active" in observed_result_dic
    assert "passive" in observed_result_dic

    assert len(observed_result_dic["active"]) == 4
    assert len(observed_result_dic["passive"]) == 219


@pytest.mark.skip("Overlaps with previous")
def test_run():
    pass
