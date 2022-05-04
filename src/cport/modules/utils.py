import pdb
import re
import os
import sys
import logging
import requests
import tempfile
from urllib import request
from cport.url import PDB_FASTA_URL, PDB_URL

log = logging.getLogger("cportlog")


def get_fasta_from_pdbid(pdb_id, chain_id):
    """Retrieve the Fasta string file given a PDBid/Chain ."""
    # https://regex101.com/r/qjjIih/1
    chain_regex = r"Chain\s(\S)|auth\s(\S)"

    target_url = f"{PDB_FASTA_URL}{pdb_id}#{chain_id}/download"
    fasta_seqs = requests.get(target_url).text

    seq_dic = {}
    for line in fasta_seqs.split(os.linesep):
        if not line:
            continue
        if line.startswith(">"):
            # -1-1 will prioritize the AUTH chain ID
            chain = re.findall(chain_regex, line)[-1][-1]
            seq_dic[chain] = line + os.linesep
        else:
            seq_dic[chain] += line

    if chain_id not in seq_dic:
        log.error(f"Could not find chain {chain_id} in {pdb_id}")
        sys.exit()
    else:
        return seq_dic[chain_id]


def get_pdb_from_pdbid(pdb_id):
    """Retrieve the PDB file from a given PDBid"""

    target_url = f"{PDB_URL}{pdb_id}.pdb"
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    request.urlretrieve(target_url, temp_file.name)

    return temp_file.name


# def func1(i, predictors_dic, params, main_dir, pdb_name):
#     predictors_dic[i] = pro_mate.run(params, main_dir, pdb_name)


# def func2(i, predictors_dic, params, main_dir, pdb_name):
#     predictors_dic[i] = meta_ppisp.run(params, main_dir, pdb_name)


# def func3(i, predictors_dic, params, main_dir, pdb_name):
#     predictors_dic[i] = spider.run(params, main_dir, pdb_name)


# def func4(i, predictors_dic, params, main_dir, pdb_name):
#     predictors_dic[i] = whiscy.run(params, main_dir, pdb_name)


# def get_processes(web_servers, predictors_dic, params, main_dir, pdb_name):
#     function_dictionary = {
#         "promate": func1,
#         "meta_ppisp": func2,
#         "spidder": func3,
#         "whiscy": func4,
#     }
#     processes = []

#     for i, server in enumerate(web_servers):
#         target_func = function_dictionary[server]
#         p = Process(
#             target=target_func, args=(i, predictors_dic, params, main_dir, pdb_name)
#         )
#         processes.append(p)

#     return processes


# def get_multiprocess_string(web_servers, main_dir):
#     temp_dir = os.path.join(main_dir, "temp")
#     print_string = ""
#     for server in web_servers:
#         sfile = server + ".status"
#         temp_file = os.path.join(temp_dir, sfile)
#         open_file = open(temp_file, "r")
#         line = open_file.readlines()[-1]
#         print_string = print_string + line
#         open_file.close()
#     return print_string


# def run(params, main_dir, pdb_name):
#     manager = multiprocessing.Manager()
#     predictors_dic = manager.dict()
#     web_servers = input_params.servers
#     n_web_servers = len(web_servers)
#     print(f"Preparing the {n_web_servers} web servers to run in parallel" + os.linesep)

#     processes = get_processes(web_servers, predictors_dic, params, main_dir, pdb_name)

#     print("Parallel run is starting" + os.linesep)
#     for p in processes:
#         p.start()

#     # Multi-print the results of the predictors
#     while any([p.is_alive() for p in processes]):
#         time.sleep(5)
#         print_string = get_multiprocess_string(web_servers, main_dir)
#         print(print_string, end=os.linesep)
#     return predictors_dic


# def get_unique_folder(tools_folder, cl_arguments):
#     if cl_arguments.pdb_file is not None:
#         pdb_name = f"{os.path.basename(cl_arguments.pdb_file)[:-4]}"
#         name_string = f"{pdb_name}_{cl_arguments.threshold}"
#     elif cl_arguments.pdb_id is not None:
#         pdb_name = f"{os.path.basename(cl_arguments.pdb_id)}"
#         name_string = f"{pdb_name}_{cl_arguments.threshold}"
#     else:
#         pdb_name = "error"
#         name_string = "run_"

#     counter = 0
#     Val = True
#     while Val:
#         random_int = random.randint(1, 9999)
#         fixed_char = format(random_int, "04d")
#         main_dir = os.path.join(tools_folder, f"{name_string}_{fixed_char}")
#         if not os.path.exists(main_dir):
#             return pdb_name, main_dir
#         if counter > 9999:
#             Val = False
#         raise AssertionError("Maximum number of folders reached")
