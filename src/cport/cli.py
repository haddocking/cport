import argparse
import json
import logging
import sys
from pathlib import Path

from cport.modules.loader import run_prediction
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

# ===========================================================================================================
# Define arguments
ap = argparse.ArgumentParser()
ap.add_argument(
    "pdb_id",
    help="",
)

ap.add_argument(
    "chain_id",
    help="",
)

ap.add_argument(
    "--fasta_file",
    help="",
)

ap.add_argument(
    "--pred",
    nargs="+",
    default=["all"],
    choices=CONFIG["predictors"] + ["all"],
    help="",
)


ap.add_argument(
    "-v",
    "--version",
    help="show version",
    action="version",
    version=f"Running {ap.prog} v{VERSION}",
)


def load_args(ap):
    """
    Load argument parser.

    Parameters
    ----------
    ap : argparse.ArgumentParser
        Argument parser.

    Returns
    -------
    cmd : argparse.Namespace
        Parsed command-line arguments.

    """
    return ap.parse_args()


# ====================================================================================#
# Define CLI
def cli(ap, main):
    """
    Command-line interface entry point.

    Parameters
    ----------
    ap : argparse.ArgumentParser
        Argument parser.
    main : function
        Main function.

    """
    cmd = load_args(ap)
    main(**vars(cmd))


def maincli():
    """Execute main client."""
    cli(ap, main)


# ====================================================================================#
# Main code
def main(pdb_id, chain_id, pred, fasta_file):
    """
    Main function.

    Parameters
    ----------
    pdb_id : str
        Protein data bank identification code.
    chain_id : str
        Chain identifier.
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
    data = {"pdb_id": pdb_id, "chain_id": chain_id, "fasta_file": fasta_file}
    result_dic = {}

    if "all" in pred:
        pred = CONFIG["predictors"]

    for predictor in pred:
        try:
            predictions = run_prediction(predictor, **data)
            result_dic[predictor] = predictions
        except Exception as e:
            log.error(f"Error running {predictor}")
            log.error(e)
            sys.exit()

    # Ouput results #==================================================================#
    format_output(result_dic, output_fname="cport.csv")


if __name__ == "__main__":
    sys.exit(maincli())
