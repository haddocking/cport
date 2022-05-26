# Test if the cons_ppisp prediction is working
from pathlib import Path

import pytest

from cport.modules.cons_ppisp import ConsPPISP


@pytest.fixture
def precalc_result():
    return Path(Path(__file__).parents[1], "tests/test_data/cons_ppisp_result.txt")


@pytest.fixture
def cons_ppisp():
    yield ConsPPISP("1PPE", "E")


@pytest.mark.skip("Cannot guarantee that the cons-PPISP server is up")
def test_submit():
    pass


def test_retrieve_prediction_link(cons_ppisp):
    page_text = "This is a page that exists and will have results"
    observed_download_url = cons_ppisp.retrieve_prediction_link(page_text=page_text)
    expected_download_url = "This is a page that exists and will have results"
    assert observed_download_url == expected_download_url


@pytest.mark.skip("Cannot test the download")
def test_download_results():
    pass


def test_parse_prediction(cons_ppisp, precalc_result):
    observed_result_dic = cons_ppisp.parse_prediction(test_file=precalc_result)

    assert "active" in observed_result_dic
    assert "passive" in observed_result_dic

    assert len(observed_result_dic["active"]) == 22
    assert len(observed_result_dic["passive"]) == 120


@pytest.mark.skip("Overlaps with previous")
def test_run():
    pass
