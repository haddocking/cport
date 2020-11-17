#!/usr/bin/env python3

import multiprocessing
import sys
from multiprocessing import Process
from IPython import embed
from tools import parser
from send_file import meta_ppisp, pro_mate, spider
import argparse
from tools import threshold
from tools import calc_sasa
from tools import residiues_distance, predictors
from tools import reconstract_pdb
from tools import save_csv
import os
import random


def run(params, main_dir):
    def func1(i, re):
        print("s1")
        re[i] = pro_mate.run(params, main_dir)
        print("e1")

    def func2(i, re):
        print("s2")
        re[i] = meta_ppisp.run(params, main_dir)
        print("e2")

    def func3(i, re):
        print("s3")
        re[i] = spider.run(params, main_dir)
        print("e3")

    manager = multiprocessing.Manager()
    predictors_dic = manager.dict()

    p1 = Process(target=func1, args=(0, predictors_dic))
    p1.start()
    p2 = Process(target=func2, args=(1, predictors_dic))
    p2.start()
    p3 = Process(target=func3, args=(2, predictors_dic))
    p3.start()
    p1.join()
    p2.join()
    p3.join()

    return predictors_dic


def get_unique_folder(tools_dir):
    while True:
        random_int = random.randint(1, 10000)
        main_dir = os.path.join(tools_dir, "run_{}".format(random_int))
        if not os.path.exists(main_dir):
            return main_dir


if __name__ == "__main__":

    try:
        '''This is the main directory of the python script. 
        Even if you run the script from a different directory,  
        it can use external files like threshold.stats and residue distance calculations'''
        tools_dir = os.path.dirname(os.path.realpath(__file__))

        '''I use run_dir to create a random directory with the name run_x. 
        The function generates unique names and makes sure that the directory does not exist.'''
        run_dir = get_unique_folder(tools_dir)
        if not os.path.exists(run_dir):
            os.mkdir(run_dir)

        """Command-line arguments"""
        if len(sys.argv) > 1:
            arg_parser = argparse.ArgumentParser()

            """The chain id and the threshold are optional arguments.
            If you don't set the threshold,
            it will automatically use 3: very sensitive (recommended from the Cport webserver)
            """
            # I am not sure what to do if you don't set a chain id
            arg_parser.add_argument('-chain_id', help="optional argument")
            arg_parser.add_argument('-threshold', help="optional preset to 3", type=int, default=3)

            """Select between ID and FILE.
            example for id:   id -pdb_id 1PPE
            example for file: file -pdb ./1PPE.pdb -seq ./seq.fasta -al FASTA """
            subparsers = arg_parser.add_subparsers(help='Choose between id and file')

            group1 = subparsers.add_parser('id', help='id help')
            group1.add_argument('-pdb_id', help="pid", required=True)

            group2 = subparsers.add_parser('file', help='file help')
            group2.add_argument('-pdb', help="fpdb", required=True)
            group2.add_argument('-seq', help="fseq", required=True)
            group2.add_argument('-al', help="alformat", required=True)

            """This is a silent argument. It does not affect the input arguments. 
            I use this argument later to distinguish the method you use"""
            group2.add_argument('-pdb_id', help=argparse.SUPPRESS, default=None)

            args = arg_parser.parse_args()
        else:
            raise AssertionError("Choose between id and file or use -h for help")

        """I save all the input files and settings in this object.
        The object will be the same if you choose ID or FILE.
        pdb_file, sequence_file, alignment_format, chain_id, threshold"""
        input_params = parser.run(args, run_dir)

        """
        This is a hard-coded part of the script. 
        I use it to save time when I already have the files from the webservers.
        I will delete it later
        run_dir = os.path.join(tools_dir, "run_test")
        temp_dir = os.path.join(run_dir, "temp")

        ppisp_temp_dir = os.path.join(temp_dir, "PPISP.pdb")
        spidder_temp_dir = os.path.join(temp_dir, "SPPIDER.pdb")
        promate_temp_dir = os.path.join(temp_dir, "ProMate.pdb")

        from tools import pdb, predictors

        pdb_file1 = pdb.from_file(spidder_temp_dir, name="SPPIDER", main_dir=run_dir)
        pdb_file2 = pdb.from_file(promate_temp_dir, name="ProMate", main_dir=run_dir)
        pdb_file3 = pdb.from_file(ppisp_temp_dir, name="PPISP", main_dir=run_dir)
        web_results = [predictors.Predictor(pdb=pdb_file1, success=True),
                       predictors.Predictor(pdb=pdb_file2, success=True),
                       predictors.Predictor(pdb=pdb_file3, success=True)]
        predictors_list = threshold.run(web_results, tools_dir, run_dir)
        """

        """
        I use the required input parameters for each web server. 
        The result is a PDB object.
        I save each PDB file in a directory called temp.
        The name of the PDB is the same as the name of the webserver.
        This function makes each web server run in parallel to save time.
        If you think it is useless, I can remove it. 
        Return a list of Predictor Objects. 
        Each Predictor object:
        pdb : The PDB file from the webserver
        cutoff_rank : An empty list, it will be updated later in the script from threshold file
        cutoff_score : An empty list, it will be updated later in the script from threshold file
        success : If the webserver run successfully (True/False)
        cutoff_surface : 15 (I copied it from Cport)
        passive_radius : 6.5 (I copied it from Cport)
        active_res : An empty list, it will be updated later in the script
        passive_res : An empty list will be updated later in the script
        name : The name of the webserver
        """
        web_results = run(input_params, main_dir=run_dir)

        """
        Identifies if the predictor ran successfully.
        Set up the thresholds based on the successful predictors and the input of the user.
        Updates the cutoff_rank and cutoff_score of the predictor Objects
        """
        predictors_list = threshold.run(web_results.values(), tools_dir, run_dir)

        """
        Solvent Accessible Surface Area calculations
        (You must install freesasa) 
        I copied the script from WHISCY
        Return a list of  residue numbers
        I filter the residues based on the value of relative mainchain and relative sidechain 
        Both values must be greater or equal to 15 (I copied the value from Cport)
        In some cases freesasa return N/A I am not sure what I should do, for now I remove these residue
        """
        surface = calc_sasa.run(input_params.pdb_file)

        """
        Distance calculations between two residues 
        I use the c++ script from Cport
        In my case, I had to recompile the script. You can find the script in tools/resdist
        Returns a list of tuples.
        Each tuple contain two residue numbers and the distance between them
        """
        distance_list = residiues_distance.run(input_params, tools_dir, run_dir)

        """
        Update the active and passive residues for each predictor object
        I use various filters copied from Cport
        More details in predictors.py script
        """
        updated_predictors = predictors.update_res(predictor_list=predictors_list,
                                                   surface=surface,
                                                   distance_list=distance_list)

        """
        I combine the active and passive residues from all the predictors
        I create a final PDB file with scores on the b-factor column
        """
        reconstract_pdb.run(predictors_list=updated_predictors, main_dir=run_dir)

        """
        A table with all the residue numbers and predictors
        I mark the active residues with + and the passive residues with -
        """
        save_csv.run(updated_predictors, input_params.pdb_file, run_dir)

    except AssertionError as ae:
        print(ae)
        raise SystemExit()
