# Test if the ispred4 prediction is working
from pathlib import Path

import pytest

from cport.modules.ispred4 import Ispred4


@pytest.fixture
def precalc_result():
    return Path(Path(__file__).parents[1], "tests/test_data/ispred4_result.txt")


@pytest.fixture
def ispred4():
    yield Ispred4("1PPE", "E")


@pytest.mark.skip("Cannot guarantee that the ISPRED4 server is up")
def test_submit():
    pass


def test_retrieve_prediction_link(ispred4):
    test_url = "https://ispred4.biocomp.unibo.it/ispred/default/job_summary?jobid=c789-edt-093c"
    page_text = "Truly anything that does not represent the webpage without results"
    observed_link = ispred4.retrieve_prediction_link(url=test_url, page_text=page_text)
    expected_link = "https://ispred4.biocomp.unibo.it/ispred/default/downloadjob?jobid=c789-edt-093c"
    assert observed_link == expected_link


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
