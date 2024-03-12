"""Test if the meta_ppisp prediction is working."""

from pathlib import Path

import pytest

from cport.modules.psiver import Psiver


@pytest.fixture
def precalc_result():
    return Path(Path(__file__).parents[1], "tests/test_data/psiver_result.txt")


@pytest.fixture
def psiver():
    yield Psiver("tests/test_data/1PPE.pdb", "E")


@pytest.mark.skip("PSIVER offline")
def test_submit(psiver):
    summary_url = psiver.submit()
    assert isinstance(summary_url, str)


@pytest.mark.skip("PSIVER offline")
def test_retrieve_prediction_link(psiver):
    page_text = "All the results are available now."
    observed_download_url = psiver.retrieve_prediction_link(page_text=page_text)
    expected_download_url = "All the results are available now."
    assert observed_download_url == expected_download_url


@pytest.mark.skip("PSIVER offline")
def test_download_results():
    pass


@pytest.mark.skip("PSIVER offline")
def test_parse_prediction(psiver, precalc_result):
    observed_result_dic = psiver.parse_prediction(test_file=precalc_result)

    assert "active" in observed_result_dic
    assert "passive" in observed_result_dic

    assert len(observed_result_dic["active"]) == 164
    assert len(observed_result_dic["passive"]) == 58


@pytest.mark.skip("PSIVER offline")
def test_run():
    pass
