import argparse
import logging

import os
import sys
from cport.version import VERSION

# from cport.modules.tools import (
#     calc_sasa,
#     parser,
#     predictors,
#     reconstruct_pdb,
#     residiues_distance,
#     save_csv,
#     threshold,
#     validations,
# )
# from cport.modules.utils import get_unique_folder, run
from cport.modules.whiscy import Whiscy
from cport.modules.scriber import Scriber
from cport.modules.ispred4 import Ispred4
from cport.modules.sppider import Sppider


# Setup logging
log = logging.getLogger("cportlog")
ch = logging.StreamHandler()
formatter = logging.Formatter(
    " [%(asctime)s %(module)s:L%(lineno)d %(levelname)s] %(message)s"
)
ch.setFormatter(formatter)
log.addHandler(ch)

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
    "-v",
    "--version",
    help="show version",
    action="version",
    version=f"Running {ap.prog} v{VERSION}",
)


def load_args(ap):
    """Load argument parser"""
    return ap.parse_args()


# ====================================================================================#
# Define CLI
def cli(ap, main):
    """Command-line interface entry point."""
    cmd = load_args(ap)
    main(**vars(cmd))


def maincli():
    """Execute main client."""
    cli(ap, main)


# ====================================================================================#
# Main code
def main(pdb_id, chain_id):

    # Start #=========================================================================#
    log.setLevel("DEBUG")
    log.info("-" * 42)
    log.info(f"          Welcome to CPORT v{VERSION}")
    log.info("-" * 42)

    # Run whiscy
    whiscy = Whiscy(pdb_id, chain_id)
    whiscy_predictions = whiscy.run()
    log.info(whiscy_predictions)

    # Run SCRIBER
    scriber = Scriber(pdb_id, chain_id)
    scriber_predictions = scriber.run()
    log.info(scriber_predictions)

    # Run ISPRED4
    ispred4 = Ispred4(pdb_id, chain_id)
    ispred4_predictions = ispred4.run()
    log.info(ispred4_predictions)

    # Run SPPIDER
    sppider = Sppider(pdb_id, chain_id)
    sppider_predictions = sppider.run()
    log.info(sppider_predictions)

    # try:
    #     # Main directory of the project
    #     cport_dir = os.path.dirname(os.path.realpath(__file__))

    #     """Command-line arguments"""
    #     if len(sys.argv) > 1:
    #         arg_parser = argparse.ArgumentParser()

    #         # All of the arguments are set as optional
    #         # They are validated in a later process
    #         arg_parser.add_argument(
    #             "-chain_id", help="optional argument", dest="chain_id"
    #         )
    #         arg_parser.add_argument(
    #             "-threshold",
    #             help="optional preset to 3",
    #             type=int,
    #             default=3,
    #             dest="threshold",
    #         )
    #         arg_parser.add_argument(
    #             "-pdb_id", help="give the id of the pdb XXXX", dest="pdb_id"
    #         )
    #         arg_parser.add_argument(
    #             "-pdb_file",
    #             help="load the pdb from a local file",
    #             type=validations.pdb_assertions,
    #             dest="pdb_file",
    #         )
    #         arg_parser.add_argument(
    #             "-sequence_file",
    #             help="load the seq from a local file",
    #             type=validations.seq_assertions,
    #             dest="seq_file",
    #         )
    #         arg_parser.add_argument(
    #             "-alignment_format",
    #             help="give the format of the alignment",
    #             choices=["FASTA", "CLUSTAL", "MAF", "PHYLIP"],
    #             dest="al",
    #         )
    #         arg_parser.add_argument(
    #             "-servers",
    #             help=(
    #                 "Choose between: whiscy(1) promate(2) meta_ppisp(3) spidder(4)     "
    #                 "                                Can select by Numbers,Names       "
    #                 "                               Can also use range ex 1:4 (All"
    #                 " servers)                                       Default value: All"
    #             ),
    #             nargs="+",
    #             default=["all"],
    #         )

    #         cl_arguments = arg_parser.parse_args()
    #         validations.argument_assertions(cl_arguments)
    #     else:
    #         raise AssertionError("Please provide pdb_id or pdb_file")

    #     # Generation of a random and unique directory run_*
    #     pdb_name, run_dir = get_unique_folder(cport_dir, cl_arguments)
    #     if not os.path.exists(run_dir):
    #         os.mkdir(run_dir)

    #     # Parse the input arguments in the object
    #     # Convert to the required formats
    #     print("Preparing the input files" + os.linesep)
    #     input_params = parser.run(cl_arguments, run_dir)
    #     print("Input files are ready" + os.linesep)

    #     # Multiprocessing function, webservers in parallel run
    #     # The outcome of the predictors is stored in a list of objects
    #     web_results = run(input_params, main_dir=run_dir, pdb_name=pdb_name)
    #     n_web_servers = len(web_results.values())
    #     print(f"Number of webservers: {n_web_servers}" + os.linesep)
    #     n_success = sum([i.success for i in web_results.values()])
    #     print(f"Successful predictors: {n_success}" + os.linesep)

    #     # Add the threshold values based on the successful predictors
    #     print(
    #         "Update the threshold values based on the successful predictors"
    #         + os.linesep
    #     )
    #     predictors_list = threshold.run(
    #         web_results.values(), cport_dir, run_dir, input_params.threshold
    #     )

    #     # Solvent Accessible Surface Area calculations
    #     # Return a list of residues and the values
    #     # In some cases freesasa return N/A
    #     # I am not sure what I should do, for now I remove these residue
    #     # Freesasa needs to be installed
    #     print("Calculate solvent accessible surface area" + os.linesep)
    #     surface = calc_sasa.run(input_params.pdb_file)

    #     # Distance Calculations between two residues (list of tuples)
    #     # The tools/resdist must be recompiled
    #     print("Calculate the residues distance" + os.linesep)
    #     distance_list = residiues_distance.run(input_params, cport_dir)

    #     # Update the active and passive residues using filters from Cport
    #     print(
    #         "Filter the residues based on precalculated residues and threshold"
    #         + os.linesep
    #     )

    #     fpredictors = predictors.update_res(
    #         predictor_list=predictors_list, surface=surface, distance_list=distance_list
    #     )

    #     # Reconstruction of the final pdb based on the active/passive residues
    #     print("Construct the final PDB" + os.linesep)
    #     reconstruct_pdb.run(
    #         init_pdb=input_params.pdb_file,
    #         predictors_list=fpredictors,
    #         main_dir=run_dir,
    #     )

    #     # Final table of each predictor and the active/passive residues
    #     print("Create the residues table" + os.linesep)
    #     save_csv.run(fpredictors, input_params.pdb_file, run_dir)

    #     cmd_file = os.path.join(run_dir, "cl_cmd.txt")
    #     with open(cmd_file, "w") as f:
    #         f.write(" ".join(sys.argv))
    #         f.write(os.linesep)
    #         f.write(f"Successful predictors: {n_success}")
    #     f.close()

    # except AssertionError as ae:
    #     print(ae)
    #     raise SystemExit()


if __name__ == "__main__":
    sys.exit(maincli())
