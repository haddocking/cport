
from pathlib import Path
import numpy as np
import time

import pandas as pd
import glob
import matplotlib.pyplot as plt


from sklearn.metrics import (
    PrecisionRecallDisplay,
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
)

from tensorflow import keras


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



#model_path = "/Users/erdemkertmen/Desktop/cport_analysis-documentation/ml_output/KERAS_dnn_oversample_sasa/keras_classifier_scriber_ispred4_scannet_sppider1692697745_121641"
model_path = "/Users/erdemkertmen/Desktop/cport_analysis-documentation/ml_output/KERAS_dnn_oversample_sasa/keras_classifier_scriber_ispred4_scannet_sppider1692711989_668405arch2X16"
arch = "mean_value_above_treshold"

# Make master.csv
"""ready_files = glob.glob("/Users/erdemkertmen/Desktop/ligand_PDBs/validation_dataset_w_values/*_cport_ready.csv")

first_iteration = True
for f in ready_files:
    df = pd.read_csv(f)

    if first_iteration:
        main_df = df
        first_iteration = False
    else: 
        main_df = pd. concat([main_df, df], axis=0)

main_df.replace("P", 0.0, inplace=True)
main_df.replace("-", 0.0, inplace=True)
main_df.replace("A", 1.0, inplace=True)
main_df.replace("AP", 0.5, inplace=True)

main_df = main_df.astype(float)
main_df.reset_index(inplace=True, drop=True)

main_df.drop(labels="Unnamed: 0", axis="columns", inplace=True)
print(main_df.shape)"""

"""output_file = "/Users/erdemkertmen/Desktop/ligand_PDBs/validation_dataset_w_values/master.csv"
main_df.to_csv(output_file)"""

# Predict on master.csv for Alphafold

t = str(time.time()).replace(".", "_") 

# main_df = pd.read_csv("/Users/erdemkertmen/Desktop/ligand_PDBs/validation_dataset_w_values/master.csv")
main_df = pd.read_csv("/Users/erdemkertmen/Desktop/ligand_PDBs/validation_dataset_w_values/above_treshold/above_master.csv")

main_df.drop(labels="Unnamed: 0", axis="columns", inplace=True)

accuracy, precision, recall, sensitivity, specificity = {}, {}, {}, {}, {}

#model = keras.models.load_model(model_path)
        # FIX THE LAYOUT OF THE PREDICTION DICT

labels = main_df["arctic3d_interaction"]
main_df.drop(labels="arctic3d_interaction", inplace=True, axis="columns")
print(main_df)
#predictions = model.predict(main_df)

predictions = mean_calculator(main_df)


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

fig.savefig("/Users/erdemkertmen/Desktop/cport-2.0-documentation/validation_analysis/cumulative_distribution_" + t + arch + ".png")

thresholds = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 0.995]

display = PrecisionRecallDisplay.from_predictions(
        labels, predictions, name="sklearn.frompredictions"
    )
        
display.plot()
plt.savefig("/Users/erdemkertmen/Desktop/cport-2.0-documentation/validation_analysis/sklearnfrompredictions_" + t + arch + ".png")

for val in thresholds:
    prediction_classes = [
        1 if prob > val else 0 for prob in np.ravel(predictions)
    ]

    tn, fp, fn, tp = confusion_matrix(labels, prediction_classes).ravel()

    sensitivity[val] = tp / (tp + fn)
    specificity[val] = tn / (tn + fp)

    # Calculate metrics
    accuracy[val] = accuracy_score(labels, prediction_classes)
    precision[val] = precision_score(labels, prediction_classes)
    recall[val] = recall_score(labels, prediction_classes)

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

df_model.to_csv("/Users/erdemkertmen/Desktop/cport-2.0-documentation/validation_analysis/threshold_scores_" + t + arch + ".csv")

print(df_model)




