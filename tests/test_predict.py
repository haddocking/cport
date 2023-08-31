import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from cport.modules.predict import (
    format_predictions,
    mean_calculator,
    read_pred,
    scriber_ispred4_scannet_sppider,
)

DATA_DIR = Path(__file__).parents[1] / "tests/test_data"


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
def prediction_csv():
    return Path(DATA_DIR, "predictors_1PPE.csv")


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
def test_scriber_ispred4_sppider_csm_potential_scannet():
    pass


def test_scriber_ispred4_scannet_sppider(prediction_csv):
    scriber_ispred4_scannet_sppider(prediction_csv)
    expected_file = Path("output/cport_ML_scriber_ispred4_scannet_sppider.csv")
    assert expected_file.exists()


def test_mean_calculator():
    df = pd.DataFrame.from_dict(
        {"col_1": [1.0, 2.0], "col_2": [2.0, 3.0], "col_3": [3.0, 4.0]}
    )

    observed = mean_calculator(df, ["col_1", "col_2", "col_3"])
    expected = [2.0, 3.0]

    assert observed == expected
