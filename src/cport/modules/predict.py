"""Trained model prediction."""
import numpy as np
from tensorflow import keras

# best model uses scriber, ispred4, sppider, csm-potential, and scannet
model_path = "model/keras_classifier_scriber_ispred4_sppider_csm_potential_scannet/saved_model.pb"


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
        results : dict
            Updated prediction dict with the predictions from the model added.

        """
        model = keras.models.load_model(model_path)
        # check if the layout of the predictions is correct
        probabilities = model.predict(predictions)

        # ADD THESE RESULTS TO THE EXISTING TABLE
        results = [1 if prob > threshold else 0 for prob in np.ravel(probabilities)]

        return results
