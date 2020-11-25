import os

def argument_assertions(args):
    if (args.pdb_id is None) and (args.pdb_file is None):
        embed()
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