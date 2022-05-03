import re
import logging
import requests

log = logging.getLogger("cportlog")


def get_pdb_fasta(pdb_id, chain_id):
    """Retrieve the Fasta string file given PDB/Chain ."""
    target_url = (
        "https://www.rcsb.org/fasta/entry/" + pdb_id + "#" + chain_id + "/download"
    )

    temp_fasta = requests.get(target_url).text

    # https://regex101.com/r/DEQghW/1
    pattern = "(>.*auth " + chain_id.capitalize() + ".*\n[A-Z].*)"

    pdb_fasta_string = re.match("%s" % pattern, temp_fasta)[0]

    log.info(f"Selected PDB Chain:\n{pdb_fasta_string}")

    return pdb_fasta_string
