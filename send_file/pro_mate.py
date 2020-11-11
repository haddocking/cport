import requests
from urllib3 import encode_multipart_formdata
from tools import pdb, predictors
import os


def run(input_params,main_dir):
    url = "http://bioinfo41.weizmann.ac.il/promate-bin/processBSF.cgi"

    file = {'fileup': ("1PPE", input_params.pdb_file.as_string, 'text/plan'),
            'pdbId': "dmmy",
            'chain': input_params.chain_id,
            'scConf': 1,
            'sc_init': 0,
            'outFormat': 'cbOutAAFull'}

    (content, header) = encode_multipart_formdata(file)

    req = requests.post(url, data=content, headers={'Content-Type': header})

    if "href" not in req.text:
        raise AssertionError(req.text[req.text.find("<body>") + len("<body>"):req.text.find("</body>")])
    else:
        temp_url = req.url

        temp_url = temp_url[:temp_url.rfind('/')]

        results_url = temp_url + "/BSFout.AA.full.pdb"

        results_pdb = pdb.from_url(results_url, name="ProMate",main_dir=main_dir)

    return predictors.Predictor(pdb=results_pdb, success=True)
