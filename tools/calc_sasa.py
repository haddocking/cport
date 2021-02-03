import subprocess
from Bio.PDB import PDBParser
import freesasa


class ResidueSASA():
    def __init__(self, name, number, tot_rel, sd_rel, bk_rel):
        self.name = name
        self.number = number
        self.relative_total = tot_rel
        self.relative_sidechain = sd_rel
        self.relative_mainchain = bk_rel


def parse_rsa_file(rsa_values):
    """Parses a .rsa NACCESS (or freesasa) file and gets the relative SASAs"""
    residue_sasas = []
    for res_id in rsa_values:
        res = rsa_values[res_id]
        name =  res.residueType
        number = int(res.residueNumber[:3])
        # Difference between NACCESS and freesasa output
        try:
            relative_total = float(res.relativeTotal)
        except ValueError:
            relative_total = -99.9
        try:
            relative_sidechain = float(res.relativeSideChain)
        except ValueError:
            relative_sidechain = -99.9
        try:
            relative_mainchain = float(res.relativeMainChain)
        except ValueError:
            relative_mainchain = -99.9

        residue_sasas.append(ResidueSASA(name,
                                         number,
                                         relative_total,
                                         relative_sidechain,
                                         relative_mainchain))

    return residue_sasas


def run(pdb_obj):
    parser = PDBParser()
    structure = parser.get_structure(pdb_obj.name, pdb_obj.pdb_dir)
    result, sasa_classes = freesasa.calcBioPDB(structure)
    rsa_values = result.residueAreas()[pdb_obj.chain_id]

    res = parse_rsa_file(rsa_values)

    surface = []
    for s in res:
        if s.relative_mainchain >= 0.15 or s.relative_sidechain >= 0.15:
            surface.append(s.number)
    return surface
