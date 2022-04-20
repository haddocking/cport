# cport

[![python lint](https://github.com/haddocking/cport/actions/workflows/lint.yml/badge.svg)](https://github.com/haddocking/cport/actions/workflows/lint.yml)

Repository for the backend machinery of the CPORT server

## Requirements
Make sure you recompile the resdist c++ script in tools/resdist
Make sure you preinstalled freesasa

To install the dependencies use:
```
python3 -m pip install -r requirements.txt
```

Change the config.json in Cport directory 

```
{
"MUSCLE": "$CPORTPATH/tools/muscle3"
  }
```

## Command line arguments

###To execute the script, you need to run the cport.py file

Then you must choose between a pdb id or a local file

For the id, you  need to give the ID of the pdb and the chain id:

```
./cport.py -pdb_id XXXX -chain X
```
For the local file, you need to give the pdb file, the chain id, the sequence file, and the alignment format:

```
./cport.py -pdb_file *.pdb -chain X -sequence_file *.txt -alignment_format * 
```

###You can select which web servers to use with -servers

To see the available webservers use :
```
./cport.py -h
```

You can use numbers:
```
./cport.py -pdb_id 1PPE -chain_id E -servers 1 3 4
```
Range of numbers:
```
./cport.py -pdb_id 1PPE -chain_id E -servers 1:4
```
Names:
```
./cport.py -pdb_id 1PPE -chain_id E -servers whiscy spidder
```

The available webservers can 
