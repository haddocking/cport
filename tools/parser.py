from tools import pdb,seq
from IPython import embed
import os


class InputParams:
    def __init__(self, pdb_file, sequence_file, alignment_format, chain_id, threshold,servers):
        self.pdb_file = pdb_file
        self.sequence_file = sequence_file
        self.alignment_format = alignment_format
        self.chain_id = chain_id
        self.threshold = threshold
        self.name = pdb_file.name
        self.servers = servers

    def print_args(self):
        print(
            self.pdb_file,
            self.sequence_file,
            self.chain_id,
            self.alignment_format,
            self.threshold,
            self.servers)


def select_servers(choice_list):
    servers = {
        1: "whiscy",
        2: "promate",
        3: "meta_ppisp",
        4: "spidder"}

    server_selection = []

    if choice_list == "all":
        server_selection = list(servers.values())

    else:
        for selection in choice_list:
            try:
                n = int(selection)
                server_selection.append(servers[n])
            except:
                split_selection = selection.split(":")
                if len(split_selection) > 1:
                    min_val = int(min(selection.split(":")))
                    max_val = int(max(selection.split(":"))) + 1
                    server_selection.extend([servers[int(n)] for n in range(min_val, max_val)])
                else:
                    if selection.lower() in servers.values():
                        server_selection.append(selection.lower())
                    else:
                        raise AssertionError("Server not found in the list")

    server_selection = list(set(server_selection))
    return server_selection


def run(argv, main_dir):
    servers = select_servers(argv.servers)

    # Using the PDB ID will download the Sequence and the PDB file
    if argv.pdb_id is not None:

        alignment_format = "FASTA"
        print("Downloading the PDB file\n")
        pdb_file = pdb.fetch_from_id(argv.pdb_id, main_dir,argv.chain_id)
        print("PDB file is ready\n")
        chain_id = argv.chain_id

        # If the chain id is not set will stop
        # If the pdb contains one chain will use that one
        if chain_id is None:
            chain_id = pdb_file.get_chain_ids()
            if len(chain_id) == 1:
                print("Only one Chain id found {} - Selected chain: {}\n".format(chain_id[0]),chain_id[0])
                chain_id = chain_id[0]
            else:
                raise AssertionError(
                    "{} chain ids found specify one with -chain_id {}".format(len(chain_id), " or ".join(chain_id)))

        print("Downloading the Sequence file\n")
        # Using HSSP file from the web returns a PHYLSEQ for WHISCY
        sequence_file = seq.fetch_from_id(argv.pdb_id,alignment_format,main_dir,pdb_file,chain_id)
        print("Sequence file is ready\n")

    else:
        # PDB file given
        name =os.path.basename(argv.pdb_file).split(".")[0]
        pdb_file = pdb.from_file(argv.pdb_file, name, main_dir=main_dir)
        print("PDB file is ready\n")
        chain_id = argv.chain_id

        # If the chain id is not set will stop
        # If the pdb contains one chain will use that one
        if chain_id is None:
            chain_id = pdb_file.get_chain_ids()
            if len(chain_id) == 1:
                print("Only one Chain id found {} - Selected chain: {}\n".format(chain_id[0],chain_id[0]))
                chain_id = chain_id[0]
            else:
                raise AssertionError(
                    "{} chain ids found specify one with -chain_id {}\n".format(len(chain_id), " or ".join(chain_id)))
        print("Preparing the Sequence file \n")
        # Converts the sequence file to match the format of WHISCY
        sequence_file = seq.from_file(argv.seq_file,name,main_dir,argv.al,pdb_file,chain_id)
        alignment_format = sequence_file.format
        print("Sequence file is ready\n")

    threshold = argv.threshold

    input_params = InputParams(pdb_file,
                               sequence_file,
                               alignment_format,
                               chain_id,
                               threshold,
                               servers)

    return input_params
