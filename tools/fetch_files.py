from tools import pdb
from urllib import request
from IPython import embed

def fetch_sequence(pdb_id):
    seq_url = "http://www.uniprot.org/uniprot/?query=database%3A%28type%3Apdb+{}%29&format=fasta".format(pdb_id)
    return request.urlopen(seq_url).read().decode("utf-8")


def fetch_pdb(pdb_id,chain,main_dir):
    pdb_url = "http://files.rcsb.org/view/{}.pdb".format(pdb_id)
    pdb_string = request.urlopen(pdb_url).read().decode("utf-8")
    final_string = ""
    if chain is None:
        for line in pdb_string.split("\n"):
            if line.startswith("ATOM") | line.startswith("TER") | line.startswith("END"):
                final_string += "{}\n".format(line)
    else:
        for line in pdb_string.split("\n"):
            if line.startswith("ATOM") | line.startswith("TER"):
                chain_in_line = line[21]
                if chain is not chain_in_line: continue
                final_string += "{}\n".format(line)
            if line.startswith("END"):
                final_string += "{}\n".format(line)

    name = pdb_id
    return pdb.from_string(final_string,name,main_dir=main_dir)
