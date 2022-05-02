import argparse
import multiprocessing
import os
import random
import sys
import time
from multiprocessing import Process

from send_file import meta_ppisp, pro_mate, spider, whiscy
from . import (
    calc_sasa,
    parser,
    predictors,
    reconstruct_pdb,
    residiues_distance,
    save_csv,
    threshold,
    validations,
)


def func1(i, predictors_dic, params, main_dir, pdb_name):
    predictors_dic[i] = pro_mate.run(params, main_dir, pdb_name)


def func2(i, predictors_dic, params, main_dir, pdb_name):
    predictors_dic[i] = meta_ppisp.run(params, main_dir, pdb_name)


def func3(i, predictors_dic, params, main_dir, pdb_name):
    predictors_dic[i] = spider.run(params, main_dir, pdb_name)


def func4(i, predictors_dic, params, main_dir, pdb_name):
    predictors_dic[i] = whiscy.run(params, main_dir, pdb_name)


def get_processes(web_servers, predictors_dic, params, main_dir, pdb_name):
    function_dictionary = {
        "promate": func1,
        "meta_ppisp": func2,
        "spidder": func3,
        "whiscy": func4,
    }
    processes = []

    for i, server in enumerate(web_servers):
        target_func = function_dictionary[server]
        p = Process(
            target=target_func, args=(i, predictors_dic, params, main_dir, pdb_name)
        )
        processes.append(p)

    return processes


def get_multiprocess_string(web_servers, main_dir):
    temp_dir = os.path.join(main_dir, "temp")
    print_string = ""
    for server in web_servers:
        sfile = server + ".status"
        temp_file = os.path.join(temp_dir, sfile)
        open_file = open(temp_file, "r")
        line = open_file.readlines()[-1]
        print_string = print_string + line
        open_file.close()
    return print_string


def run(params, main_dir, pdb_name):
    manager = multiprocessing.Manager()
    predictors_dic = manager.dict()
    web_servers = input_params.servers
    n_web_servers = len(web_servers)
    print(f"Preparing the {n_web_servers} web servers to run in parallel" + os.linesep)

    processes = get_processes(web_servers, predictors_dic, params, main_dir, pdb_name)

    print("Parallel run is starting" + os.linesep)
    for p in processes:
        p.start()

    # Multi-print the results of the predictors
    while any([p.is_alive() for p in processes]):
        time.sleep(5)
        print_string = get_multiprocess_string(web_servers, main_dir)
        print(print_string, end=os.linesep)
    return predictors_dic


def get_unique_folder(tools_folder, cl_arguments):
    if cl_arguments.pdb_file is not None:
        pdb_name = f"{os.path.basename(cl_arguments.pdb_file)[:-4]}"
        name_string = f"{pdb_name}_{cl_arguments.threshold}"
    elif cl_arguments.pdb_id is not None:
        pdb_name = f"{os.path.basename(cl_arguments.pdb_id)}"
        name_string = f"{pdb_name}_{cl_arguments.threshold}"
    else:
        pdb_name = "error"
        name_string = "run_"

    counter = 0
    Val = True
    while Val:
        random_int = random.randint(1, 9999)
        fixed_char = format(random_int, "04d")
        main_dir = os.path.join(tools_folder, f"{name_string}_{fixed_char}")
        if not os.path.exists(main_dir):
            return pdb_name, main_dir
        if counter > 9999:
            Val = False
        raise AssertionError("Maximum number of folders reached")


if __name__ == "__main__":

    try:
        # Main directory of the project
        cport_dir = os.path.dirname(os.path.realpath(__file__))

        """Command-line arguments"""
        if len(sys.argv) > 1:
            arg_parser = argparse.ArgumentParser()

            # All of the arguments are set as optional
            # They are validated in a later process
            arg_parser.add_argument(
                "-chain_id", help="optional argument", dest="chain_id"
            )
            arg_parser.add_argument(
                "-threshold",
                help="optional preset to 3",
                type=int,
                default=3,
                dest="threshold",
            )
            arg_parser.add_argument(
                "-pdb_id", help="give the id of the pdb XXXX", dest="pdb_id"
            )
            arg_parser.add_argument(
                "-pdb_file",
                help="load the pdb from a local file",
                type=validations.pdb_assertions,
                dest="pdb_file",
            )
            arg_parser.add_argument(
                "-sequence_file",
                help="load the seq from a local file",
                type=validations.seq_assertions,
                dest="seq_file",
            )
            arg_parser.add_argument(
                "-alignment_format",
                help="give the format of the alignment",
                choices=["FASTA", "CLUSTAL", "MAF", "PHYLIP"],
                dest="al",
            )
            arg_parser.add_argument(
                "-servers",
                help=(
                    "Choose between: whiscy(1) promate(2) meta_ppisp(3) spidder(4)     "
                    "                                Can select by Numbers,Names       "
                    "                               Can also use range ex 1:4 (All"
                    " servers)                                       Default value: All"
                ),
                nargs="+",
                default=["all"],
            )

            cl_arguments = arg_parser.parse_args()
            validations.argument_assertions(cl_arguments)
        else:
            raise AssertionError("Please provide pdb_id or pdb_file")

        # Generation of a random and unique directory run_*
        pdb_name, run_dir = get_unique_folder(cport_dir, cl_arguments)
        if not os.path.exists(run_dir):
            os.mkdir(run_dir)

        # Parse the input arguments in the object
        # Convert to the required formats
        print("Preparing the input files" + os.linesep)
        input_params = parser.run(cl_arguments, run_dir)
        print("Input files are ready" + os.linesep)

        # Multiprocessing function, webservers in parallel run
        # The outcome of the predictors is stored in a list of objects
        web_results = run(input_params, main_dir=run_dir, pdb_name=pdb_name)
        n_web_servers = len(web_results.values())
        print(f"Number of webservers: {n_web_servers}" + os.linesep)
        n_success = sum([i.success for i in web_results.values()])
        print(f"Successful predictors: {n_success}" + os.linesep)

        # Add the threshold values based on the successful predictors
        print(
            "Update the threshold values based on the successful predictors"
            + os.linesep
        )
        predictors_list = threshold.run(
            web_results.values(), cport_dir, run_dir, input_params.threshold
        )

        # Solvent Accessible Surface Area calculations
        # Return a list of residues and the values
        # In some cases freesasa return N/A
        # I am not sure what I should do, for now I remove these residue
        # Freesasa needs to be installed
        print("Calculate solvent accessible surface area" + os.linesep)
        surface = calc_sasa.run(input_params.pdb_file)

        # Distance Calculations between two residues (list of tuples)
        # The tools/resdist must be recompiled
        print("Calculate the residues distance" + os.linesep)
        distance_list = residiues_distance.run(input_params, cport_dir)

        # Update the active and passive residues using filters from Cport
        print(
            "Filter the residues based on precalculated residues and threshold"
            + os.linesep
        )

        fpredictors = predictors.update_res(
            predictor_list=predictors_list, surface=surface, distance_list=distance_list
        )

        # Reconstruction of the final pdb based on the active/passive residues
        print("Construct the final PDB" + os.linesep)
        reconstruct_pdb.run(
            init_pdb=input_params.pdb_file,
            predictors_list=fpredictors,
            main_dir=run_dir,
        )

        # Final table of each predictor and the active/passive residues
        print("Create the residues table" + os.linesep)
        save_csv.run(fpredictors, input_params.pdb_file, run_dir)

        cmd_file = os.path.join(run_dir, "cl_cmd.txt")
        with open(cmd_file, "w") as f:
            f.write(" ".join(sys.argv))
            f.write(os.linesep)
            f.write(f"Successful predictors: {n_success}")
        f.close()

    except AssertionError as ae:
        print(ae)
        raise SystemExit()
