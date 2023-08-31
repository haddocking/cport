"""Trained model prediction."""
import csv

import numpy as np
import pandas as pd
from tensorflow import keras


def mean_calculator(
    df: pd.DataFrame,
    target_predictors: list[str],
) -> list[float]:
    """Calculate the mean of the values provided for predictors."""
    mean_preds = []
    for _, row in df.iterrows():
        value = 0.0
        for predictor in target_predictors:
            value += row[predictor]
        value = value / 4
        mean_preds.append(value)
    return mean_preds


def read_pred(path: str) -> dict[str, list[str]]:
    """Read the prediction file."""
    with open(path, "r") as pred:
        reader = csv.reader(pred)
        pred_dict = {rows[0]: rows for rows in reader}

    return pred_dict


def format_predictions(pred_int_dict):
    """
    Format predictions to remove any non-numerical entry, keeps prediction scores.

    Parameters
    ----------
    pred_ind_dict : dict
        Dictionary containing the predictions.

    Output
    ------
    pred_int_dict : dict
        Dictionary containing the predictions in a binary format.
    """
    for pred in pred_int_dict:
        temp_list = pred_int_dict[pred][1:]
        pred_int_dict[pred] = temp_list

    for pred in pred_int_dict:
        if pred != "predictor":
            key = 0
            for entry in pred_int_dict[pred]:
                if entry == "P" or entry == "-" or entry == 0:
                    pred_int_dict[pred][key] = 0
                elif entry == "A":
                    pred_int_dict[pred][key] = 1
                elif entry == "AP":
                    pred_int_dict[pred][key] = 0.5
                else:
                    temp_pred = pred_int_dict[pred][key]
                    pred_int_dict[pred][key] = float(temp_pred)
                key += 1

    return pred_int_dict


def scriber_ispred4_sppider_csm_potential_scannet(prediction_csv: str, threshold=0.6):
    """Apply the `scriber_ispred4_sppider_csm_potential_scannet` model."""

    pred_res = read_pred(path=prediction_csv)
    model_path = "model/keras_classifier_scriber_ispred4_sppider_csm_potential_scannet"
    pred_dict = format_predictions(pred_res)
    predictor = pred_dict.pop("predictor")
    pred = pd.DataFrame(pred_dict)
    model = keras.models.load_model(model_path)
    # FIX THE LAYOUT OF THE PREDICTION DICT
    probabilities = model.predict(pred)  # type: ignore
    prediction = [1 if prob > threshold else 0 for prob in np.ravel(probabilities)]

    output_dic = {}

    probabilities_edit = []
    residue_edit = []
    for item in probabilities.tolist():
        probabilities_edit.append(item[0])

    for item in predictor:
        residue_edit.append(int(item))

    output_dic["threshold_pred"] = prediction
    output_dic["probabilities"] = probabilities_edit
    output_dic["residue"] = residue_edit

    save_file = "output/cport_something.csv"
    out_csv = pd.DataFrame(output_dic)
    out_csv.to_csv(save_file)


def scriber_ispred4_scannet_sppider(prediction_csv, threshold=0.6):
    """Apply the `scriber_ispred4_scannet_sppider` model."""
    pred_res = read_pred(path=prediction_csv)
    model_path = (
        "model/keras_classifier_scriber"
        + "_ispred4_scannet_sppider1692711989_668405arch2X16"
    )
    pred_dict = format_predictions(pred_res)
    predict_residue = pred_dict.pop("predictor")
    pred = pd.DataFrame(pred_dict)
    model = keras.models.load_model(model_path)
    probabilities = model.predict(pred)  # type: ignore
    mean_scores = mean_calculator(
        df=pred, target_predictors=["scriber", "ispred4", "scannet", "sppider"]
    )
    prediction = [1 if prob > threshold else 0 for prob in np.ravel(probabilities)]
    output_dic = {}

    cport_scores = []
    residue_edit = []
    for item in probabilities.tolist():
        cport_scores.append(item[0])

    for item in predict_residue:
        residue_edit.append(int(item))

    output_dic["residue"] = residue_edit
    output_dic["cport_scores"] = cport_scores
    output_dic["threshold_pred"] = prediction
    output_dic["mean_scores"] = mean_scores

    save_file = "output/cport_something_else.csv"
    out_csv = pd.DataFrame(output_dic)
    out_csv.to_csv(save_file)
