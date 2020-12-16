import os


servers = {
        1: "whiscy",
        2: "promate",
        3: "meta_ppisp",
        4: "spidder"}


def argument_assertions(args):
    if (args.pdb_id is None) and (args.pdb_file is None):
        raise AssertionError("Please provide pdb_id or pdb_file")
    elif (args.pdb_id is not None) and (args.pdb_file is not None):
        raise AssertionError("Please choose only one argument: -pdb_id or -pdb_file")
    elif (args.pdb_id is not None) and (args.pdb_file is None):
        if (args.seq_file is not None) or (args.al is not None):
            raise AssertionError("argument pdb_id does not need sequence file or alignment format")
    elif (args.pdb_id is None) and (args.pdb_file is not None):
        if (args.seq_file is None) and (args.al is None):
            raise AssertionError("Please provide sequence file and alignment format")
        elif (args.seq_file is None) and (args.al is not None):
            raise AssertionError("Please provide sequence file")
        elif (args.seq_file is not None) and (args.al is None):
            raise AssertionError("Please provide alignment format")
    if args.servers[0] != "all":
        for selection in args.servers:
            if ":" in selection:
                try:
                    numbers = [int(n) for n in selection.split(":")]
                    check = [n for n in numbers if n in range(1, max(servers.keys())+1)]
                    if not (len(numbers) == len(check)):
                        raise AssertionError("Invalid range numbers")
                except Exception:
                    raise AssertionError("Invalid range numbers")
            elif len(selection) == 1:
                if selection.isnumeric():
                    n = int(selection)
                    if not (n in range(1, max(servers.keys())+1)):
                        raise AssertionError(f"Number {selection} not in selection range")
                else:
                    raise AssertionError(f"Single value {selection} is not a number")
            else:
                if selection not in servers.values():
                    raise AssertionError(f"Server {selection} is not available")


def pdb_assertions(pdb_location):
    if not os.path.exists(pdb_location):
        raise AssertionError("PDB file does not exist")
    if not pdb_location.endswith(".pdb"):
        raise AssertionError("File extension does not match file format: PDB")
    return pdb_location


def seq_assertions(sequence_location):
    if not os.path.exists(sequence_location):
        raise AssertionError("Sequence file does not exist")
    return sequence_location
