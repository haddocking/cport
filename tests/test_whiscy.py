# Test if the whiscy prediction is working
from cport.modules.whiscy import Whiscy

import pytest


@pytest.fixture
def whiscy():
    yield Whiscy("1PPE", "E")


@pytest.mark.skip("Cannot test the submission")
def test_submit(whiscy):
    """Test the submission of the form."""
    pass


def test_retrieve_prediction(whiscy):
    """Test the retrieval of the prediction."""
    page_text = (
        '<textarea class="form-control" cols="100" id="active_list" name="active_list"'
        ' rows="3">20, 22, 25, 28, 39, 41, 64, 66, 70, 72, 73, 74, 75, 76, 77, 78, 79,'
        " 80, 81, 82, 92, 94, 95, 112, 113, 114, 115, 116, 117, 119,"
        ' 133</textarea>\n<textarea class="form-control" cols="100" id="passive_list"'
        ' name="passive_list" rows="3">18, 19, 21, 23, 24, 26, 27, 29, 30, 31, 32, 33,'
        " 34, 37, 38, 40, 42, 43, 46, 49, 50, 56, 60, 62, 63, 65, 67, 69, 71, 83, 84,"
        " 85, 90, 91, 93, 96, 97, 98, 99, 100, 101, 102, 103, 108, 110, 111, 118, 120,"
        " 121, 130, 132, 134, 135, 141, 152, 153, 154, 155, 156, 157, 158, 161, 162,"
        " 163, 193, 237</textarea>"
    )
    observed_prediction = whiscy.retrieve_prediction(page_text=page_text)

    assert "active" in observed_prediction
    assert "passive" in observed_prediction

    assert len(observed_prediction["active"]) == 31
    assert len(observed_prediction["passive"]) == 66


@pytest.mark.skip("Overlaps with previous")
def test_run(whiscy):
    """Test the execution of the module."""
    pass
