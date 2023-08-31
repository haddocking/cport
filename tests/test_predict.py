import os
import tempfile

import pytest

from cport.modules.predict import format_predictions, read_pred


@pytest.fixture
def prediction_dic():
    return {
        "predictor": ["predictor", "1", "2", "3", "4", "5", "6"],
        "ispred4": ["ispred4", "P", "P", "AP", "0", "-", "1.7"],
    }


@pytest.fixture
def formatted_prediction():
    return {
        "predictor": ["1", "2", "3", "4", "5", "6"],
        "ispred4": [0.0, 0.0, 0.5, 0.0, 0.0, 1.7],
    }


@pytest.fixture
def temp_csv():
    input_csv = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
    yield input_csv
    os.unlink(input_csv.name)


def test_read_pred(temp_csv, prediction_dic):
    contents = "predictor,1,2,3,4,5,6\nispred4,P,P,AP,0,-,1.7\n"
    temp_csv.write(contents.encode())
    temp_csv.close()

    observed = read_pred(temp_csv.name)
    expected = prediction_dic

    assert observed == expected


def test_format_predictions(prediction_dic, formatted_prediction):
    observed = format_predictions(prediction_dic)
    expected = formatted_prediction

    assert observed == expected


@pytest.mark.skip(reason="Not implemented yet.")
def test_make_prediction():
    pass
