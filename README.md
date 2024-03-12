# CPORT: Consensus Prediction Of interface Residues in Transient complexes

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![python lint](https://github.com/haddocking/cport/actions/workflows/lint.yml/badge.svg)](https://github.com/haddocking/cport/actions/workflows/lint.yml)
[![unittests](https://github.com/haddocking/cport/actions/workflows/unittests.yml/badge.svg)](https://github.com/haddocking/cport/actions/workflows/unittests.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/c4dd6c7da85847e1832b9668beb6de31)](https://www.codacy.com/gh/haddocking/cport/dashboard?utm_source=github.com&utm_medium=referral&utm_content=haddocking/cport&utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/c4dd6c7da85847e1832b9668beb6de31)](https://www.codacy.com/gh/haddocking/cport/dashboard?utm_source=github.com&utm_medium=referral&utm_content=haddocking/cport&utm_campaign=Badge_Coverage)

[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/6074/badge)](https://bestpractices.coreinfrastructure.org/projects/6074)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B%20%20%E2%97%8B%20%20%E2%97%8F-orange)](https://fair-software.eu)

## DISCLAIMER

This repository contains an **ongoing development** of the next version of CPORT, and as such it is not stable yet. The codebase might change drastically in the future.

For the current stable version, please access the web service at [https://alcazar.science.uu.nl/services/CPORT](https://alcazar.science.uu.nl/services/CPORT/).

Please also refer to the original publication:

- de Vries, S. J. & Bonvin, A. M. J. J. [CPORT: A Consensus Interface Predictor and Its Performance in Prediction-Driven Docking with HADDOCK](https://doi.org/10.1371/journal.pone.0017695). PLoS ONE vol. 6 e17695 (2011).

---

## Predictors

| Server                                                           | Status | Implemented |
| ---------------------------------------------------------------- | ------ | ----------- |
| [WHISCY](https://wenmr.science.uu.nl/whiscy/)                    | 🟢     | ✔️          |
| [SCRIBER](http://biomine.cs.vcu.edu/servers/SCRIBER/)            | 🟢     | ✔️          |
| [ISPRED4](https://ispred4.biocomp.unibo.it/ispred/default/index) | 🟢     | ✔️          |
| [SPPIDER](https://sppider.cchmc.org)                             | 🟢     | ✔️          |
| [meta-PPISP](https://pipe.rcc.fsu.edu/meta-ppisp.html)           | 🟢     | ✔️          |
| [PredUs2](http://honig.c2b2.columbia.edu/predus)                 | 🟠     |             |
| [Cons-PPISP](https://pipe.rcc.fsu.edu/ppisp.html)                | 🟢     | ✔️          |
| [PredictProtein](https://predictprotein.org)                     | 🟢     | ✔️          |
| [PSIVER](https://mizuguchilab.org/PSIVER/)                       | 🔴     | ✔️          |
| [CSM-Potential](http://biosig.unimelb.edu.au/csm_potential/)     | 🔴     | ✔️          |
| [ScanNet](http://bioinfo3d.cs.tau.ac.il/ScanNet/index_real.html) | 🟢     | ✔️          |

## Installation

Please refer to [INSTALL.md](INSTALL.md) for installation instructions.

## Example

```text
cport path/to/file/1PPE.pdb E
```

## Machine Learning based consensus prediction of interface residues

See all related data at https://github.com/haddocking/cport-data

#### `scriber_ispred4_sppider_csm_potential_scannet`

_pending_

#### `cport_ispred4_scannet_sppider`

The `cport_ispred4_scannet_sppider` model was developed to obtain the interface residues of proteins for protein docking, using the predictions of several webservers and a deep neural network. This model uses SCRIBER, SCANNET, ISPRED4, and SPPIDER.

##### Data Preparation

The training and validation data can be found in "cport/data".
Scripts for data preparetion step can be found in "cport/src/data_prep".

**_prepare_training_data.py_**: This script is used for combining the retrieved predictions of the receptors in BM5 and ARCTIC3D interface residues, and create a master ".csv" file for training the machine learning model.

**_prepare_validation_data.py_**: This script is used for combining the retrieved predictions of the Alphafold reference structures of the ligands in the BM5 and ARCTIC3D interface residues, and create a master ".csv" file for validating the machine learning model.

**_filter_pdb.py_**: This script is used on the AlphaFold validation data to distinguish between the residues according to their b-factor values. The residues with a b-factor value higher than 0.8 and below 0.8 are seperated and used for creating 2 different master ".csv" files. This is performed because the residues with lower b-factor values were not reliable for validation.

## Machine Learning Model

Scripts related to the machine learning model can be found in "cport/src/ml_models".

**_ml_dataprep.py_**: This script contains the codes for utilities used in building the model such as handling imbalance in the data, splitting the data into train-test data, etc. The default model is built and trained without any sampling on the data, with the ratio of the labels 0 and 1 being 2/1. If desired, the sampler can be used, created in lines 32-33.

**_tf_class.py_**: This is the script where the model is built and trained with the proper data.
The model is built with certain parameters to maximize the efficiency of the predictions, considering the amount of the features and the training data. These parameters can be adjusted and a new model can be created by modifiying the following lines as desired:

line 44 -> modify units=16

line 47 -> modify loop variable to create more layers

line 48 -> modify units=16

line 55 -> modify learning_rate=1e-2

After the model has been built and trained, the model and the analysis graphs are saved into the path given in line 92.
The training data for the model can be changed by changing the "pred_path" parameter in line 68.
The sampling method can be modified by changing the "sampler" parameter in line 69

**_alphafold_data_prediction.py_**: This script is used to analyze the created model using the validation data of AlphaFold proteins.

## How to contribute

Please have a look at [CONTRIBUTE](CONTRIBUTING.md)

## How to get Support

If you encounter a bug or would like to request a feature, please open an ISSUE or a PR.
