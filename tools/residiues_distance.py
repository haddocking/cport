import subprocess
import os


def get_distance_list(distance_results):
    dist_list = []
    for line in distance_results.split("\n"):
        split_line = line.split()
        res1 = int(split_line[0])
        res2 = int(split_line[1])
        distance = float(split_line[2])
        dist_list.append((res1, res2, distance))
    return dist_list


def run(input_params, tools_dir):
    pdb_dir = input_params.pdb_file.pdb_dir.replace(" ", r"\ ")
    res_dir = os.path.join(tools_dir, "tools/resdist/resdist")
    res_dir = res_dir.replace(" ", r"\ ")
    final_dir = res_dir + " {}".format(pdb_dir)
    try:
        dist = subprocess.getoutput(final_dir)
        distace_list = get_distance_list(dist)
    except Exception as er:
        raise AssertionError("Resdist did not run {}".format(er))

    return distace_list
