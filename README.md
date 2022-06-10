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
| [PredUs2](http://honig.c2b2.columbia.edu/predus)                 | 🟠     | ✔️          |
| [Cons-PPISP](https://pipe.rcc.fsu.edu/ppisp.html)                | 🟢     | ✔️          |
| [PredictProtein](https://predictprotein.org)                     | 🟢     | ✔️          |
| [PSIVER](https://mizuguchilab.org/PSIVER/)                       | 🟢     | ✔️          |
| [CSM-Potential](http://biosig.unimelb.edu.au/csm_potential/)     | 🟢     | ✔️          |

## Installation

Please refer to [INSTALL.md](INSTALL.md) for installation instructions.

## Example

```text
cport path/to/file/1PPE.pdb E
```

## How to contribute

Please have a look at [CONTRIBUTE](CONTRIBUTING.md)

## How to get Support

If you encounter a bug or would like to request a feature, please open an ISSUE or a PR.
