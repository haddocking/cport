# Test if the sppider prediction is working
from pathlib import Path

import pytest

from cport.modules.sppider import Sppider


@pytest.fixture
def precalc_result():
    return Path(Path(__file__).parents[1], "tests/test_data/sppider_result.txt")


@pytest.fixture
def sppider():
    yield Sppider("1PPE", "E")


@pytest.mark.skip("Cannot guarantee that the SPPIDER server is up")
def test_submit():
    pass


def test_retrieve_prediction_link(sppider):
    page_text = "<meta http-equiv=Refresh content=0;URL=http://polyview.cchmc.org/cgi-bin/pr_picture.cgi?PDBName=1ppe&FName=387265&AddInfo=int>"
    observed_download_url = sppider.retrieve_prediction_link(page_text=page_text)
    expected_download_url = "http://polyview.cchmc.org/cgi-bin/pr_picture.cgi?PDBName=1ppe&amp;FName=387265&amp;AddInfo=int"
    assert observed_download_url == expected_download_url


def test_parse_prediction(sppider, precalc_result):
    page_text = precalc_result.read_text()

    observed_result_dic = sppider.parse_prediction(page_text=page_text)

    assert "active" in observed_result_dic
    assert "passive" in observed_result_dic

    assert len(observed_result_dic["active"]) == 29
    assert len(observed_result_dic["passive"]) == 0


@pytest.mark.skip("Overlaps with previous")
def test_run():
    pass
