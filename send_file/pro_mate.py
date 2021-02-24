import requests
from urllib3 import encode_multipart_formdata
from tools import pdb, predictors
import os
import time

def wait_promate(url,content,header, temp_file):
    waiting = 0
    while True:
        req = requests.post(url, data=content, headers={'Content-Type': header})

        if waiting > 120 * 60:
            print("Promate: Server timeout", file=open(temp_file, "a"))
            return "http://Failed.com"

        if "href"  in req.text:
            print(f"Promate: URL found!", file=open(temp_file, "a"))
            return req.url

        else:
            print("Promate: Send the files again: {}".format(waiting),
                  file=open(temp_file, "a"))
        time.sleep(5)
        waiting += 5

def run(input_params, main_dir,pdb_name):
    url = "http://bioinfo41.weizmann.ac.il/promate-bin/processBSF.cgi"
    name = input_params.name
    pdb_string = input_params.pdb_file.as_string

    file = {'fileup': (name, pdb_string, 'text/plan'),
            'pdbId': "dmmy",
            'chain': input_params.chain_id,
            'scConf': 1,
            'sc_init': 0,
            'outFormat': 'cbOutAAFull'}

    temp_dir = os.path.join(main_dir, "temp")
    temp_file = os.path.join(temp_dir, "promate.status")
    print("Promate: Start", file=open(temp_file, "a"))

    (content, header) = encode_multipart_formdata(file)
    req = requests.post(url, data=content, headers={'Content-Type': header})
    print("Promate: Processing", file=open(temp_file, "a"))

    temp_url = wait_promate(url,content,header,temp_file)
    if "Failed" in temp_url:
        print("Promate: Failed !!",
              file=open(temp_file, "a"))
        return predictors.Predictor(pdb=input_params.pdb_file, name="ProMate", success=False)
    else:

        time.sleep(10)
        temp_url = temp_url[:temp_url.rfind('/')]

        results_url = temp_url + "/BSFout.AA.full.pdb"

        results_pdb = pdb.from_url(results_url,
                                   name=f"{pdb_name}_ProMate",
                                   main_dir=main_dir)
        print(f"Promate: Finished successfully {results_url}", file=open(temp_file, "a"))
        return predictors.Predictor(pdb=results_pdb,name="ProMate", success=True)
