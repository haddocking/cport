"""Trained model prediction."""
import csv

import numpy as np
import pandas as pd
from tensorflow import keras

# best model uses scriber, ispred4, sppider, and scannet
model_path = "model/keras_classifier_scriber_ispred4_scannet_sppider1692711989_668405arch2X16/"


class ModelPredict:

    def mean_calculator(df):

        """
        Decides the active residues  by calculating the mean of the values provided for predictors 

        Parameters
        ------
        df:
            dataframe of predictors and the values for each residue

        Outputs
        ------
        mean_preds:
            list of mean prediction values for each residue in the correct order
        
        """

        mean_preds = []
        for i, row in df.iterrows():
            value = 0.0
            value += row["scriber"]
            value += row["sppider"]
            value += row["ispred4"]
            value += row["scannet"]
            value = value / 4
            mean_preds.append(value)
        return mean_preds

    def read_pred(path):

        with open(path, "r", encoding="utf-8-sig") as pred:
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
                    if entry == "A":
                        pred_int_dict[pred][key] = 1
                    if entry == "AP":
                        pred_int_dict[pred][key] = 0.5
                    else:
                        temp_pred = pred_int_dict[pred][key]
                        pred_int_dict[pred][key] = float(temp_pred)
                    key += 1

        return pred_int_dict

    def prediction(predictions, threshold=0.6):
        """
        Take the different results and create a final prediction.

        Parameters
        ----------
        predictions : dict
            Predictions made by the different servers.
        threshold : int
            Value to use as a threshold, defaults to 0.6.

        Returns
        -------
        results : list
            List of the predictions for each residue of the PDB.

        """
        pred_dict = ModelPredict.format_predictions(predictions)
        predictor = pred_dict.pop("predictor")
        pred = pd.DataFrame(pred_dict)
        model = keras.models.load_model(model_path)
        # FIX THE LAYOUT OF THE PREDICTION DICT

        print(pred)

        cport_scores = model.predict(pred)
        mean_scores = ModelPredict.mean_calculator(pred)

        results = [1 if prob > threshold else 0 for prob in np.ravel(cport_scores)]

        return results, cport_scores, predictor, mean_scores
