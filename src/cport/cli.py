"""Main CLI."""
import argparse
import json
import logging
import sys
from pathlib import Path

from cport.modules.loader import run_prediction
from cport.modules.predict import (
    scriber_ispred4_scannet_sppider,
    scriber_ispred4_sppider_csm_potential_scannet,
)
from cport.modules.threadreturn import ThreadReturnVal
from cport.modules.utils import format_output
from cport.version import VERSION

# Setup logging
log = logging.getLogger("cportlog")
ch = logging.StreamHandler()
formatter = logging.Formatter(
    " [%(asctime)s %(module)s:L%(lineno)d %(levelname)s] %(message)s"
)
ch.setFormatter(formatter)
log.addHandler(ch)


CONFIG = json.load(open(Path(Path(__file__).parents[2], "etc/config.json")))

ML_PREDICTION = {
    scriber_ispred4_scannet_sppider: {
        "needed": ["scriber", "ispred4", "scannet", "sppider"],
    },
    scriber_ispred4_sppider_csm_potential_scannet: {
        "needed": ["scriber", "ispred4", "scannet", "sppider", "csm_potential"],
    },
}

# ===========================================================================================================
# Define arguments
argument_parser = argparse.ArgumentParser()
argument_parser.add_argument(
    "pdb_file",
    help="",
)

argument_parser.add_argument(
    "chain_id",
    help="",
)

argument_parser.add_argument(
    "--pdb_id",
    help="",
)

argument_parser.add_argument(
    "--fasta_file",
    help="",
)

argument_parser.add_argument(
    "--pred",
    nargs="+",
    default=["validated"],
    choices=CONFIG["predictors"] + ["all"] + ["validated"],
    help="",
)


argument_parser.add_argument(
    "-v",
    "--version",
    help="show version",
    action="version",
    version=f"Running {argument_parser.prog} v{VERSION}",
)


def load_args(arguments):
    """
    Load argument parser.

    Parameters
    ----------
    arguments : argparse.ArgumentParser
        Argument parser.

    Returns
    -------
    cmd : argparse.Namespace
        Parsed command-line arguments.

    """
    return arguments.parse_args()


# ====================================================================================#
# Define CLI
def cli(arguments, main_func):
    """
    Command-line interface entry point.

    Parameters
    ----------
    arguments : argparse.ArgumentParser
        Argument parser.
    main_func : function
        Main function.

    """
    cmd = load_args(arguments)
    main_func(**vars(cmd))


def maincli():
    """Execute main client."""
    cli(argument_parser, main)


# ====================================================================================#
# Main code
def main(pdb_file, chain_id, pdb_id, pred, fasta_file):
    """
    Execute main function.

    Parameters
    ----------
    pdb_id : str
        Protein data bank identification code.
    chain_id : str
        Chain identifier.
    pdb_file : str
        Path to pdb file.
    pred : list
        List of predictors to run.
    fasta_file : str
        Fasta file.

    """
    # Start #=========================================================================#
    log.setLevel("DEBUG")
    log.info("-" * 42)
    log.info(f" Welcome to CPORT v{VERSION}")
    log.info("-" * 42)

    # Run predictors #================================================================#

    data = {
        "pdb_id": pdb_id,
        "chain_id": chain_id,
        "fasta_file": fasta_file,
        "pdb_file": pdb_file,
    }
    result_dic = {}

    if "all" in pred:
        pred = CONFIG["predictors"]

    if "validated" in pred:
        pred = [
            "scriber",
            "sppider",
            "scannet",
            "ispred4",
        ]

    threads = {}

    # prepare a dict of predictor initializations.
    for predictor in pred:
        threads[predictor] = ThreadReturnVal(
            target=run_prediction, args=predictor, kwargs=data, name=predictor
        )

    for predictor in threads:
        try:
            # initiate threads for predictors.
            threads[predictor].start()
        except Exception as thrown_exception:
            log.error(f"Error running {predictor}")
            log.error(thrown_exception)
            sys.exit(1)

    for predictor in threads:
        # retrieve results from predictions with modified join
        result_dic[predictor] = threads[predictor].join()

    # Ouput results #==================================================================#
    filename = Path(pdb_file)

    save_file = "output/predictors_" + filename.stem + ".csv"
    format_output(
        result_dic,
        output_fname=save_file,
        pdb_file=pdb_file,
        chain_id=chain_id,
    )

    # Use the ML model to make the prediction #========================================#
    for predictor in ML_PREDICTION:
        # Check if all the features are there
        if all(item in result_dic for item in ML_PREDICTION[predictor]["needed"]):
            log.info(f"Running ML predictor {predictor.__name__}")
            predictor(save_file)
        else:
            log.warning(
                "Not all needed predictors returned a result, skipping ML model."
            )
            log.warning(
                "Missing predictors: " + ", ".join(ML_PREDICTION[predictor]["needed"])
            )


if __name__ == "__main__":
    sys.exit(maincli())
