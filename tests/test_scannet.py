# Test if the scannet prediction is working
from pathlib import Path

import pytest

from cport.modules.scannet import ScanNet


@pytest.fixture
def precalc_result():
    return Path(Path(__file__).parents[1], "tests/test_data/scannet_result.pdb")


@pytest.fixture
def scannet():
    yield ScanNet("tests/test_data/1PPE.pdb", "A")


@pytest.mark.skip("Cannot guarantee that the cons-PPISP server is up")
def test_submit():
    pass


def test_retrieve_prediction_link(scannet):
    page_text = "stringContainingTheWholePdbFile"
    observed_download_url = scannet.retrieve_prediction_link(page_text=page_text)
    expected_download_url = "stringContainingTheWholePdbFile"
    assert observed_download_url == expected_download_url


@pytest.mark.skip("Cannot test the download")
def test_download_results():
    pass


def test_parse_prediction(scannet, precalc_result):
    observed_result_dic = scannet.parse_prediction(test_file=precalc_result)

    assert "active" in observed_result_dic
    assert "passive" in observed_result_dic

    assert len(observed_result_dic["active"]) == 19
    assert len(observed_result_dic["passive"]) == 204


@pytest.mark.skip("Overlaps with previous")
def test_run():
    pass
