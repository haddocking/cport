#!/usr/bin/env python3

import multiprocessing
import sys
from multiprocessing import Process
from IPython import embed
from tools import parser
from send_file import meta_ppisp, pro_mate, spider, whiscy
import argparse
from tools import threshold
from tools import calc_sasa
from tools import residiues_distance, predictors
from tools import reconstruct_pdb
from tools import save_csv
from tools import validations
import os
import random
import time


def func1(i, predictors_dic, params, main_dir):
    predictors_dic[i] = pro_mate.run(params, main_dir)


def func2(i, predictors_dic, params, main_dir):
    predictors_dic[i] = meta_ppisp.run(params, main_dir)


def func3(i, predictors_dic, params, main_dir):
    predictors_dic[i] = spider.run(params, main_dir)


def func4(i, predictors_dic, params, main_dir):
    predictors_dic[i] = whiscy.run(params, main_dir)


def get_processes(web_servers, predictors_dic, params, main_dir):
    processes = []
    for i, server in enumerate(web_servers):
        if server == "promate":
            p = Process(target=func1, args=(i, predictors_dic, params, main_dir))
        elif server == "meta_ppisp":
            p = Process(target=func2, args=(i, predictors_dic, params, main_dir))
        elif server == "spidder":
            p = Process(target=func3, args=(i, predictors_dic, params, main_dir))
        elif server == "whiscy":
            p = Process(target=func4, args=(i, predictors_dic, params, main_dir))
        else:
            raise AssertionError("Webserver not in the list")
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


def run(params, main_dir):
    manager = multiprocessing.Manager()
    predictors_dic = manager.dict()
    web_servers = ["promate", "meta_ppisp", "spidder", "whiscy"]
    #web_servers = ["promate"]

    print("Preparing the {} web servers to run in parallel\n".format(len(web_servers)))
    processes = get_processes(web_servers, predictors_dic, params, main_dir)

    print("Parallel run is starting\n")
    for p in processes:
        p.start()

    # Multi-print the results of the predictors
    while any([p.is_alive() for p in processes]):
        time.sleep(5)
        print_string = get_multiprocess_string(web_servers, main_dir)
        print(print_string, end="\n")
    return predictors_dic


def get_unique_folder(tools_folder):
    while True:
        random_int = random.randint(1, 10000)
        main_dir = os.path.join(tools_folder, "run_{}".format(random_int))
        if not os.path.exists(main_dir):
            return main_dir


if __name__ == "__main__":

    try:
        # Main directory of the project
        tools_dir = os.path.dirname(os.path.realpath(__file__))

        """Command-line arguments"""
        if len(sys.argv) > 1:
            arg_parser = argparse.ArgumentParser()

            # All of the arguments are set as optional, they are validated in a later process
            arg_parser.add_argument('-chain_id', help="optional argument", dest="chain_id")
            arg_parser.add_argument('-threshold', help="optional preset to 3", type=int, default=3, dest="threshold")
            arg_parser.add_argument('-pdb_id', help="give the id of the pdb XXXX", dest="pdb_id")
            arg_parser.add_argument('-pdb_file', help="load the pdb from a local file", type=validations.pdb_assertions,
                                    dest="pdb_file")
            arg_parser.add_argument('-sequence_file', help="load the seq from a local file",
                                    type=validations.seq_assertions, dest="seq_file")
            arg_parser.add_argument('-alignment_format', help="give the format of the alignment",
                                    choices=["FASTA", "CLUSTAL", "MAF", "PHYLIP"], dest="al")
            cl_arguments = arg_parser.parse_args()
            validations.argument_assertions(cl_arguments)
        else:
            raise AssertionError("Please provide pdb_id or pdb_file")

        # Generation of a random and unique directory run_*
        run_dir = get_unique_folder(tools_dir)
        if not os.path.exists(run_dir):
            os.mkdir(run_dir)

        # Parse the input arguments in the object
        # There are functions to make sure tha the files has the required formats
        print("Preparing the input files\n")
        input_params = parser.run(cl_arguments, run_dir)
        print("Input files are ready\n")

        # Multiprocessing function to send the files in the different webservers in parallel
        # The outcome of the predictors is stored in a list of objects
        web_results = run(input_params, main_dir=run_dir)
        print("Number of webservers: {}\n".format(len(web_results.values())))
        print("Successful predictors: {}\n".format(sum([i.success for i in web_results.values()])))

        # Add the threshold values based on the successful predictors
        print("Update the threshold values based on the successful predictors\n")
        predictors_list = threshold.run(web_results.values(), tools_dir, run_dir)

        # Solvent Accessible Surface Area calculations as a list of residues and the values
        # In some cases freesasa return N/A I am not sure what I should do, for now I remove these residue
        # Freesasa needs to be installed
        print("Calculate solvent accessible surface area\n")
        surface = calc_sasa.run(input_params.pdb_file)

        # Distance Calculations between two residues (list of tuples)
        # The tools/resdist must be recompiled
        print("Calculate the residues distance\n")
        distance_list = residiues_distance.run(input_params, tools_dir, run_dir)

        # Update the active and passive residues for each predictor using filters from Cport
        print("Filter the residues based on precalculated residues and threshold\n")
        updated_predictors = predictors.update_res(predictor_list=predictors_list,
                                                   surface=surface,
                                                   distance_list=distance_list)

        # Reconstruction of the final pdb based on the active/passive residues
        print("Construct the final PDB\n")
        reconstruct_pdb.run(init_pdb = input_params.pdb_file,predictors_list=updated_predictors, main_dir=run_dir)

        # Final table of each predictor and the active/passive residues
        print("Create the residues table\n")
        save_csv.run(updated_predictors, input_params.pdb_file, run_dir)

    except AssertionError as ae:
        print(ae)
        raise SystemExit()
