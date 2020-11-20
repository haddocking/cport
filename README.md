# cport
Repository for the backend machinery of the CPORT server

## Requirements
Make sure you recompile the resdist c++ script in tools/resdist
Make sure you preinstalled freesasa

To install the dependencies use:
```
python3 -m pip install -r requirements.txt
```

## Command line arguments

To execute the script, you need to run the cport.py file

Then you must choose between a pdb id or a local file

For the id, you only need to give the ID of the pdb:

```
./cport.py -pdb_id XXXX
```
For the local file, you need to give the pdb file, the sequence file, and the alignment format:

```
./cport.py -pdb_file *.pdb -sequence_file *.txt -alignment_format * 
```

The chain id and threshold are optional arguments:
```
./cport.py -chain_id * -threshold * -pdb_id XXXX
```
or 
```
./cport.py -chain_id * -threshold * -pdb_file *.pdb -sequence_file *.txt -alignment_format *
```

