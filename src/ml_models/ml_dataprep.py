import pandas as pd
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class DataPrep:
    def imbalance_adjust(features, labels, scale, predictors):
        """
        Balance a dataset for classification.

        Parameters
        ----------
        features : dict
            Dictionary of predictions by individual predictors.
        labels : list
            List of true interfaces.
        scale : bool
            If True, a standardscaler will be applied
        predictors : list
            List containing the predictors with which to perform the undersampling.

        Output
        ------
        X_under : dict
            Undersampled dict of predictions.
        y_under : list
            Undersampled list of ground truths
        """
        # sampler = RandomUnderSampler(sampling_strategy="majority")
        sampler = RandomOverSampler(sampling_strategy="minority")
        scaler = StandardScaler()

        if scale:
            features = scaler.fit_transform(features)

        X_under, y_under = sampler.fit_resample(features, labels)

        X_under = pd.DataFrame(X_under, columns=predictors)

        y_under = pd.DataFrame(y_under, columns=["arctic3d_interaction"])

        return X_under, y_under

    def train_test(
        pred_path="/Users/erdemkertmen/Desktop/combined_dataset_r_u/master.csv",
        sampler=True,
        scale=False,
        predictors=["scriber", "ispred4", "sppider", "scannet", "arctic3d_interaction"],
    ):
        """
        Split a dataset into a train and test set.

        Parameters
        ----------
        pred_path : str
            Path to the predictions list.
        undersample : bool
            If True, the dataset will be undersampled, for imbalanced data
        scale : bool
            If True, a standardscaler will be applied
        predictors : list
            List containing the predictors with which to create the sets.

        Output
        ------
        X_train : dict
            Dictionary of predictions.
        X_test : dict
            Dictionary of predictions
        y_train : list
            List of ground truths
        y_test : list
            List of ground truths
        features : dict
            Dictionary of all predictions
        labels : list
            List of all ground truths
        """
        """train = pd.read_csv(
            pred_path,
            names=[
                "residue",
                "true_int",
                "scriber",
                "ispred4",
                "sppider",
                "cons_ppisp",
                "predictprotein",
                "csm_potential",
                "scannet",
                "sasa",
            ],
            skiprows=1,
        )"""

        train = pd.read_csv(
            pred_path,
            names=[
                "scriber",
                "ispred4",
                "sppider",
                # "csm_potential",
                "scannet",
                "arctic3d_interaction",
            ],
            skiprows=1,
        )
        # print(train)

        for name in train:
            if name not in predictors and name != "arctic3d_interaction":
                train.pop(name)

        # train.pop("residue")
        features = train.copy(deep=True)
        labels = features.pop("arctic3d_interaction")
        # print(features)
        # print(labels)

        if sampler:
            # create imblanced train-test splits
            Z_train, X_test, z_test, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=1
            )
            # balance only the training set, so test is still unbalanced for final validation
            X_train, y_train = DataPrep.imbalance_adjust(
                Z_train, z_test, scale, predictors
            )

        else:
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2
            )
        # print(X_train)
        # print(X_test)
        # print(y_train.value_counts())
        # print(y_test.value_counts())
        return X_train, X_test, y_train, y_test, features, labels
