"""Test if the meta_ppisp prediction is working"""
from pathlib import Path

import pytest

from cport.modules.meta_ppisp import MetaPPISP


@pytest.fixture
def precalc_result():
    return Path(Path(__file__).parents[1], "tests/test_data/meta_ppisp_result.txt")


@pytest.fixture
def meta_ppisp():
    yield MetaPPISP("1PPE", "E")


@pytest.mark.skip("Cannot guarantee that the meta-PPISP server is up")
def test_submit():
    pass


def test_retrieve_prediction_link(meta_ppisp):
    page_text = "This is a page that exists and will have results"
    observed_download_url = meta_ppisp.retrieve_prediction_link(page_text=page_text)
    expected_download_url = "This is a page that exists and will have results"
    assert observed_download_url == expected_download_url


@pytest.mark.skip("Cannot test the download")
def test_download_results():
    pass


def test_parse_prediction(meta_ppisp, precalc_result):
    observed_result_dic = meta_ppisp.parse_prediction(test_file=precalc_result)

    assert "active" in observed_result_dic
    assert "passive" in observed_result_dic

    assert len(observed_result_dic["active"]) == 15
    assert len(observed_result_dic["passive"]) == 127


@pytest.mark.skip("Overlaps with previous")
def test_run():
    pass
