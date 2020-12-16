import subprocess


class ResidueSASA():
    def __init__(self, chain_id, name, number, tot_rel, sd_rel, bk_rel):
        self.chain_id = chain_id
        self.name = name
        self.number = number
        self.relative_total = tot_rel
        self.relative_sidechain = sd_rel
        self.relative_mainchain = bk_rel


def parse_rsa_file(rsa_file_name):
    """Parses a .rsa NACCESS (or freesasa) file and gets the relative SASAs"""
    residue_sasas = []
    with open(rsa_file_name, "rU") as input_handle:
        for line in input_handle:
            if line.startswith("RES"):
                if line[13] == ' ':
                    # Avoid alternative positions
                    name = line[4:7]
                    chain_id = line[8]
                    number = int(line[9:13])
                    # Difference between NACCESS and freesasa output
                    try:
                        relative_total = float(line[23:29])
                    except ValueError:
                        relative_total = -99.9
                    try:
                        relative_sidechain = float(line[36:42])
                    except ValueError:
                        relative_sidechain = -99.9
                    try:
                        relative_mainchain = float(line[49:55])
                    except ValueError:
                        relative_mainchain = -99.9

                    residue_sasas.append(ResidueSASA(chain_id,
                                                     name,
                                                     number,
                                                     relative_total,
                                                     relative_sidechain,
                                                     relative_mainchain))

    return residue_sasas


def run(pdb_obj):
    pdb_file_name = pdb_obj.pdb_dir
    if " " in pdb_file_name:
        pdb_file_name = pdb_file_name.replace(" ", r"\ ")
    output_file_name = pdb_file_name.replace(".pdb", ".rsa")
    cmd = "freesasa {} -n 20\
     --format=rsa\
      --radii=naccess -o {}".format(pdb_file_name, output_file_name)
    try:
        subprocess.run(cmd, shell=True)
    except Exception:
        subprocess.check_call(cmd, shell=True)

    res = parse_rsa_file(pdb_obj.pdb_dir.replace(".pdb", ".rsa"))

    surface = []
    for s in res:
        if s.relative_mainchain >= 15 or s.relative_sidechain >= 15:
            surface.append(s.number)

    return surface
