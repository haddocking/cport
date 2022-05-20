import logging
from functools import partial
import pdb

from cport.modules.error import IncompleteInputError
from cport.modules.ispred4 import Ispred4
from cport.modules.scriber import Scriber
from cport.modules.whiscy import Whiscy
from cport.modules.sppider import Sppider
from cport.modules.cons_ppisp import Cons_ppisp
from cport.modules.meta_ppisp import Meta_ppisp
from cport.modules.predus2 import Predus2
from cport.modules.predictprotein import Predictprotein

log = logging.getLogger("cportlog")


def run_whiscy(pdb_id, chain_id):
    """Run the WHISCY predictor."""
    whiscy = Whiscy(pdb_id, chain_id)
    whiscy_predictions = whiscy.run()
    log.info(whiscy_predictions)


def run_ispred4(pdb_id, chain_id):
    """Run the ispred4 predictor."""
    ispred4 = Ispred4(pdb_id, chain_id)
    ispred4_predictions = ispred4.run()
    log.info(ispred4_predictions)


def run_scriber(pdb_id, chain_id):
    """Run the scriber predictor."""
    scriber = Scriber(pdb_id, chain_id)
    scriber_predictions = scriber.run()
    log.info(scriber_predictions)


def run_sppider(pdb_id, chain_id):
    """Run the sppider predictor."""
    sppider = Sppider(pdb_id, chain_id)
    sppider_predictions = sppider.run()
    log.info(sppider_predictions)


def run_cons_ppisp(pdb_id, chain_id):
    """Run the cons-ppisp predictor"""
    cons_ppisp = Cons_ppisp(pdb_id, chain_id)
    cons_ppisp_predictions = cons_ppisp.run()
    log.info(cons_ppisp_predictions)


def run_meta_ppisp(pdb_id, chain_id):
    """Run the meta-ppisp predictor"""
    meta_ppisp = Meta_ppisp(pdb_id, chain_id)
    meta_ppisp_predictions = meta_ppisp.run()
    log.info(meta_ppisp_predictions)


def run_predus2(pdb_id, chain_id):
    """Run the PredUs2 predictor."""
    predus2 = Predus2(pdb_id, chain_id)
    predus2_predictions = predus2.run()
    log.info(predus2_predictions)


def run_predictprotein(pdb_id, chain_id):
    """Run the Predict Protein predictor"""
    predictprotein = Predictprotein(pdb_id, chain_id)
    predictprotein_predictions = predictprotein.run()
    log.info(predictprotein_predictions)


def run_placeholder(fasta_str):
    """Run the placeholder predictor."""
    log.info("Placeholder predictor")
    log.info(f"fasta_str: {fasta_str}")


PDB_PREDICTORS = {
    "whiscy": run_whiscy,
    "scriber": run_scriber,
    "ispred4": run_ispred4,
    "sppider": run_sppider,
    "cons_ppisp": run_cons_ppisp,
    "meta_ppisp": run_meta_ppisp,
    "predus2": run_predus2,
    "predictprotein": run_predictprotein,
}

FASTA_PREDICTORS = {"placeholder": run_placeholder}


def run_prediction(prediction_method, **kwargs):
    """Select predictors to run."""
    if prediction_method in PDB_PREDICTORS:
        if not kwargs["pdb_id"]:
            raise IncompleteInputError(
                predictor_name=prediction_method, missing="pdb_id"
            )

        if not kwargs["chain_id"]:
            raise IncompleteInputError(
                predictor_name=prediction_method, missing="chain_id"
            )

        predictor_func = partial(
            PDB_PREDICTORS[prediction_method],
            pdb_id=kwargs["pdb_id"],
            chain_id=kwargs["chain_id"],
        )

    elif prediction_method in FASTA_PREDICTORS:
        if not kwargs["fasta_file"]:
            raise IncompleteInputError(
                predictor_name=prediction_method, missing="fasta_file"
            )
        predictor_func = partial(
            FASTA_PREDICTORS[prediction_method], fasta_str=kwargs["fasta_file"]
        )
    else:
        raise ValueError(f"Unknown prediction method: {prediction_method}")

    log.info(f"Running method: {prediction_method}")
    predictor_func()
