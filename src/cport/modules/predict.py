"""Trained model prediction."""
import numpy as np
from tensorflow import keras

# best model uses scriber, ispred4, sppider, csm-potential, and scannet
model_path = "model/keras_classifier_scriber_ispred4_sppider_csm_potential_scannet/"


class ModelPredict:
    def prediction(predictions, threshold=0.8):
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
        model = keras.models.load_model(model_path)
        # FIX THE LAYOUT OF THE PREDICTION DICT
        probabilities = model.predict(predictions)

        results = [1 if prob > threshold else 0 for prob in np.ravel(probabilities)]

        return results
