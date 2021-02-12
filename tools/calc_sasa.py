from tools import haddock_calc_sasa


class ResidueSASA():
    def __init__(self, name, number, sd_rel, bk_rel):
        self.name = name
        self.number = number
        self.relative_sidechain = sd_rel
        self.relative_mainchain = bk_rel


def parse_rsa_file(rsa_values):
    """Parses a .rsa NACCESS (or freesasa) file and gets the relative SASAs"""
    residue_sasas = []
    for res_id in rsa_values:
        res = rsa_values[res_id]
        name =  res['name']
        number = int(res_id.strip()[:3])
        # Difference between NACCESS and freesasa output
        try:
            relative_sidechain = float(res['side_chain_rel'])
        except ValueError:
            relative_sidechain = -99.9
        try:
            relative_mainchain = float(res['main_chain_rel'])
        except ValueError:
            relative_mainchain = -99.9

        residue_sasas.append(ResidueSASA(name,
                                         number,
                                         relative_sidechain,
                                         relative_mainchain))

    return residue_sasas


def run(pdb_obj):
    rsa_values = haddock_calc_sasa.get_accessibility(pdb_obj.pdb_dir)
    res = parse_rsa_file(rsa_values[pdb_obj.chain_id])
    surface = []
    for s in res:
        if s.relative_mainchain >= 15 or s.relative_sidechain >= 15:
            surface.append(s.number)
    return surface
