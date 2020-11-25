import requests
from urllib3 import encode_multipart_formdata
from tools import pdb, predictors
from urllib import request
import time
import ssl
import os

ssl._create_default_https_context = ssl._create_unverified_context


def wait(url,temp_file):
    waiting = 0
    while True:
        html_string = request.urlopen(url).read().decode("utf-8")
        if "404 Not Found" in html_string:
            raise AssertionError("Url not found")
        if waiting > 120 * 60:
            raise Exception('Timeout on the server')
        if "pdb" in html_string:
            return html_string
        else:
            print("MEAT PPISP: proccesing {}".format(waiting), file=open(temp_file, "a"))
            #print(waiting)
            #print(html_string)
        time.sleep(5)
        waiting += 5


def run(input_params,main_dir):
    url = 'https://pipe.rcc.fsu.edu/cgi-bin/meta-ppisp/run'

    file = {'userfile': (input_params.name, input_params.pdb_file.as_string, 'text/plan'),
            'submitter': "1PPE",
            'pChain': input_params.chain_id}

    (content, header) = encode_multipart_formdata(file)

    temp_dir = os.path.join(main_dir, "temp")
    temp_file = os.path.join(temp_dir, "meta_ppisp.status")
    print("META PPISP: Start", file=open(temp_file, "a"))

    req = requests.post(url, data=content, headers={'Content-Type': header}, verify=False)

    for line in req.text.split("\n"):
        if "href" in line:
            start_tag = 'href="'
            end_tag = '">'
            url = line[line.index(start_tag) + len(start_tag):line.index(end_tag)]

    html_string = wait(url,temp_file)

    pdb_url=""
    for line in html_string.split("\n"):
        if ("pdb" in line) & ("http" in line):
            pdb_url = line

    if pdb_url != "":
        results_pdb = pdb.from_url(pdb_url, name="PPISP",main_dir=main_dir)
        print("META PPISP: Finished successfully", file=open(temp_file, "a"))
        return predictors.Predictor(pdb=results_pdb, success=True)
    else:
        print("META PPISP: Failed", file=open(temp_file, "a"))
        return predictors.Predictor(pdb=input_params.pdb_file, success=False)
