# Test if the ispred4 prediction is working
from pathlib import Path

import pytest

from cport.modules.ispred4 import Ispred4
from cport.url import ISPRED4_URL


@pytest.fixture
def precalc_result():
    return Path(Path(__file__).parents[1], "tests/test_data/ispred4_result.txt")


@pytest.fixture
def ispred4():
    yield Ispred4("tests/test_data/1PPE.pdb", "E")


@pytest.mark.skip("Cannot guarantee that the ISPRED4 server is up")
def test_submit():
    pass


def test_retrieve_prediction_link(ispred4):
    page_text = (
        "https://ispred4.biocomp.unibo.it/ispred/default/"
        "job_summary?jobid=c789-edt-093c"
    )
    observed_download_url = ispred4.retrieve_prediction_link(page_text=page_text)
    expected_download_url = f"{ISPRED4_URL}downloadjob?jobid=c789-edt-093c"
    assert observed_download_url == expected_download_url


@pytest.mark.skip("Cannot test the download")
def test_download_results():
    pass


def test_parse_prediction(ispred4, precalc_result):
    observed_result_dic = ispred4.parse_prediction(precalc_result)

    assert "active" in observed_result_dic
    assert "passive" in observed_result_dic

    assert len(observed_result_dic["active"]) == 21
    assert len(observed_result_dic["passive"]) == 93


@pytest.mark.skip("Overlaps with previous")
def test_run():
    pass
