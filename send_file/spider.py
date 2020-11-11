import time
from urllib import request
import requests
from urllib3 import encode_multipart_formdata

from tools import pdb,predictors
import os


def wait_spider(url):
    waiting = 0
    while True:
        html_string = request.urlopen(url).read().decode("utf-8")
        if "404 Not Found" in html_string:
            raise AssertionError("Url not found")
        if waiting > 120 * 60:
            raise Exception("Timeout on the cons-PPISP server")
        if "pr_picture.cgi" in html_string:
            for line in html_string.split("\n"):
                if "pr_picture.cgi" in line:
                    new_url = line.split("URL=")[1]
                    new_url = new_url.split('"')[0]
                    return new_url
        else:
            print(waiting)
            print(html_string)
        time.sleep(5)
        waiting += 5


def run(input_params,main_dir):

    url = 'http://sppider.cchmc.org/cgi-bin/int_recognition.cgi'

    fields = {"PDBFileName": ("1PPE", input_params.pdb_file.as_string, 'text/plan'),
              "Version": "2",
              "Trade": "0.5",
              "Email": "",
              "PDBres": "on"}

    (content, header) = encode_multipart_formdata(fields)

    req = requests.post(url, data=content, headers={'Content-Type': header}, verify=False)

    temp_url = req.text.split('<a href="')[1].split('">')[0]

    result_url = wait_spider(temp_url)

    for line in request.urlopen(result_url).readlines():
        if "sppider.pdb" in line.decode("utf-8"):
            line = line.decode("utf-8")
            pdb_url = line.split('<a href="')[1].split('"')[0]
            results_pdb = pdb.from_url(pdb_url, name= "SPPIDER",main_dir=main_dir)
            return predictors.Predictor(pdb=results_pdb, success=True)

