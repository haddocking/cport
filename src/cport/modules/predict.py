"""Trained model prediction."""
import csv

import numpy as np
import pandas as pd
from tensorflow import keras

# best model uses scriber, ispred4, sppider, csm-potential, and scannet
model_path = "model/keras_classifier_scriber_ispred4_sppider_csm_potential_scannet/"


# class ModelPredict:
def read_pred(path: str) -> dict[str, list[str]]:
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


def make_prediction(predictions, threshold=0.6):
    """
    Take the different results and create a final prediction.

    Parameters
    ----------
    predictions : dict
        Predictions made by the different servers.
    threshold : int
        Value to use as a threshold, defaults to 0.8.

    Returns
    -------
    results : list
        List of the predictions for each residue of the PDB.

    """
    pred_dict = format_predictions(predictions)
    predictor = pred_dict.pop("predictor")
    pred = pd.DataFrame(pred_dict)
    model = keras.models.load_model(model_path)
    # FIX THE LAYOUT OF THE PREDICTION DICT
    probabilities = model.predict(pred)  # type: ignore

    results = [1 if prob > threshold else 0 for prob in np.ravel(probabilities)]

    return results, probabilities, predictor
