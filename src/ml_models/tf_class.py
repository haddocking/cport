import sys
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# import seaborn as sns
import tensorflow as tf

# from matplotlib import rcParams
from sklearn.metrics import (
    PrecisionRecallDisplay,
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
)

# sys.path is a list of absolute path strings
sys.path.append(".")
# trunk-ignore(flake8/E402)
from ml_dataprep import DataPrep


class KERASPred:
    def build_model(input_dim=4):
        model = tf.keras.Sequential()
        """
        Build a model for a TensorFlow Neural Network with desired input dimensions.

        Parameters
        ----------
        input_dim : 
            Used to create the input layer according to nuber of predictors used. It can be modified according to the input number.

        Output
        ------
        model : model
            Model with a certain combination of the hyperparameters.
        """
        # input layer based on number of.  used predictors
        model.add(
            tf.keras.layers.Dense(units=16, input_dim=input_dim, activation="tanh")
        )

        for i in range(2):
            model.add(tf.keras.layers.Dense(units=16, activation="tanh"))
            #model.add(tf.keras.layers.Dropout(0.2))

        # output neuron, singular sigmoid as classification is binary
        model.add(tf.keras.layers.Dense(1, activation="sigmoid")) #sigmoid

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-2),
            loss=tf.keras.losses.mean_squared_error,
            #loss=tf.keras.losses.binary_crossentropy,
            metrics=[
                tf.keras.metrics.BinaryAccuracy(name="accuracy"),
                tf.keras.metrics.Precision(name="precision"),
                tf.keras.metrics.Recall(name="recall"),
                tf.keras.metrics.AUC(name="auc", curve="PR"),
            ],
        )
        return model

    def tf_main(
        pred_path="/Users/erdemkertmen/Desktop/cport-2.0-documentation/training_dataset_w_values/master.csv",
        sampler=False,
        scale=False,
        predictors=["ispred4", "scriber", "scannet", "sppider"], # ["ispred4", "scriber", "scannet", "csm_potential", "sppider"]
    ):
        """
        Create and train a TensorFlow Neural Network on a specified dataset.

        Parameters
        ----------
        pred_path : list
            Path to the dataset to be used for training.
        sampling : bool
            If True, the dataset will be undersampled, for imbalanced data.
        scale : bool
            If True, a standardscaler will be applied on the dataset, for imbalanced data.

        Output
        ------
        df_model : dict
            Dictionary with the statistical scores of the different thresholds.
        """
        accuracy, precision, recall, sensitivity, specificity = {}, {}, {}, {}, {}
        stat_dict = {}
        output = "ml_outputs/KERAS_dnn_nosampling/"
        output_name = "_".join(predictors)
        
        output_name = output_name + str(time.time()).replace(".", "_") 

        X_train, X_test, y_train, y_test, features, labels = DataPrep.train_test(
            pred_path=pred_path,
            sampler=sampler,
            scale=scale,
            predictors=predictors,
        )
        callback = tf.keras.callbacks.EarlyStopping(monitor="val_auc", patience=3)
        
        model = KERASPred.build_model(input_dim=4)
        for e in range(10):
            model.fit(
                X_train, y_train, epochs=1, validation_data=(X_test, y_test)
                #callbacks=[callback],
            )

            eval_result = model.evaluate(X_test, y_test)
            print("[test loss, test accuracy]:", eval_result)

            predictions = model.predict(X_test).ravel()
        
        model.save(filepath=output + "keras_classifier_" + output_name)
        min_pred = min(predictions)
        max_pred = max(predictions)
        # print(min_pred)
        # print(max_pred)
        

        predictionstrain = model.predict(X_train).ravel()
        # print(min(predictionstrain))
        # print(max(predictionstrain))

        # Scale the prediction data according to minmax values in the training
        predictions = (predictions - min(predictionstrain)) / (max(predictionstrain) - min(predictionstrain))

        
        fig, ax1 = plt.subplots()

        ax2 = ax1.twinx()
        hists, bins , p = ax1.hist(predictions, 50)
        x, y2 = [0], [0]
        for i, height in enumerate(hists):
            a = np.mean(bins[i:i+2])
            x.append(a)
            y = height + y2[-1]
            y2.append(y)


        y2 = [1 - (y / len(predictions)) for y in y2]
        print(y2)
        ax2.plot(x, y2, 'b-')
        ax2.set_ylim(0.0, 1.0)

        fig.savefig(output + "KERAS_PR_"+output_name+"cumulative_graph.png")



        plt.hist(predictions, 50)
        plt.savefig(output + "KERAS_PR_"+output_name+"prediction_distribution.png")

        predicted_classes = np.argmax(y_test, axis=-1)

        thresholds = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 0.995]

        display = PrecisionRecallDisplay.from_predictions(
                y_test, predictions, name="sklearn.frompredictions"
            )
        
        display.plot()
        plt.savefig(output + "KERAS_PR_"+output_name+"sklearnfrompredictions.png")

        for val in thresholds:
            prediction_classes = [
                1 if prob > val else 0 for prob in np.ravel(predictions)
            ]

            tn, fp, fn, tp = confusion_matrix(y_test, prediction_classes).ravel()

            sensitivity[val] = tp / (tp + fn)
            specificity[val] = tn / (tn + fp)

            # Calculate metrics
            accuracy[val] = accuracy_score(y_test, prediction_classes)
            precision[val] = precision_score(y_test, prediction_classes)
            recall[val] = recall_score(y_test, prediction_classes)

            """display = PrecisionRecallDisplay.from_predictions(
                y_test, prediction_classes, name="KERAS_" + str(val)
            )

            display.plot()
            plt.savefig(output + "KERAS_PR_"+output_name+"_threshold_" + str(val) + ".png")"""

        df_model = pd.DataFrame(
            index=thresholds,
            columns=["Accuracy", "Precision", "Recall", "Sensitivity", "Specificity"],
        )
        df_model["Accuracy"] = accuracy.values()
        df_model["Precision"] = precision.values()
        df_model["Recall"] = recall.values()
        df_model["Sensitivity"] = sensitivity.values()
        df_model["Specificity"] = specificity.values()

        df_model.to_csv(output + "threshold_scores_" + output_name + ".csv")

        print(df_model)


predictor_list = [
    "scriber",
    "ispred4",
    "sppider",
    "cons_ppisp",
    "predictprotein",
    "csm_potential",
    "scannet",
    "sasa",
]

KERASPred.tf_main(predictors=["scriber", "ispred4", "scannet", "sppider"])

"""
combinations = [
    ["scriber", "ispred4", "sppider", "cons_ppisp", "csm_potential", "sasa"],
    ["scriber","sppider", "predictprotein", "csm_potential", "sasa"],
    ["scriber", "ispred4", "sppider", "cons_ppisp", "predictprotein", "csm_potential"],
    ["scriber", "ispred4", "cons_ppisp", "csm_potential", "scannet"],
    ["scriber", "ispred4", "predictprotein", "scannet"],
]

for comb in combinations:
    KERASPred.tf_main(predictors=comb)
"""
"""
combinations = {}

for length in range(3, len(predictor_list) + 1):
    combinations[length] = list(itertools.combinations(predictor_list, length))

for key in combinations:
    for comb in combinations[key]:
        KERASPred.tf_main(predictors=comb)


KERASPred.tf_main()
"""