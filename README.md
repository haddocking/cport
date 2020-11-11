# cport
Repository for the backend machinery of the CPORT server

## Requirements
Make sure you recompile the resdist c++ script in tools/resdist
Make sure you preinstalled freesasa

## Command line arguments

To execute the script, you need to run the __init__.py file

Then you must choose between a pdb id or a local file

For the id, you only need to give the ID of the pdb:

```
python3 __init__.py id -pdb_id XXXX
```
For the local file, you need to give the pdb file, the sequence file, and the alignment format:

```
python3 __init__.py file -pdb *.pdb -seq *.txt -al * 
```

The chain id and threshold are optional arguments and must be placed at the start:
```
python3 __init__.py -chain_id -threshold id -pdb_id XXXX
```
or 
```
python3 __init__.py -chain_id -threshold file -pdb *.pdb -seq *.txt -al * 
```

