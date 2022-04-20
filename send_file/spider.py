import os
import time
from urllib import request

import lxml.html
import requests
from urllib3 import encode_multipart_formdata

from tools import pdb, predictors


def wait_spider(url, temp_file):
    waiting = 0
    while True:
        html_string = request.urlopen(url).read().decode("utf-8")
        if "404 Not Found" in html_string:
            print("SPPIDER: URL not found {}".format(url), file=open(temp_file, "a"))
            return "http://Failed.com"
        if waiting > 120 * 60:
            print("SPPIDER: Server timeout", file=open(temp_file, "a"))
            return "http://Failed.com"
        if "pr_picture.cgi" in html_string:
            for line in html_string.split(os.linesep):
                if "pr_picture.cgi" in line:
                    new_url = line.split("URL=")[1]
                    new_url = new_url.split('"')[0]
                    return new_url
        else:
            print("SPPIDER: proccesing {}".format(waiting), file=open(temp_file, "a"))
        time.sleep(5)
        waiting += 5


def run(input_params, main_dir, pdb_name):

    url = "http://sppider.cchmc.org/cgi-bin/int_recognition.cgi"
    name = input_params.name
    pdb_string = input_params.pdb_file.as_string
    fields = {
        "PDBFileName": (name, pdb_string, "text/plan"),
        "Version": "2",
        "Trade": "0.5",
        "Email": "",
        "PDBres": "on",
    }

    (content, header) = encode_multipart_formdata(fields)
    temp_dir = os.path.join(main_dir, "temp")
    temp_file = os.path.join(temp_dir, "spidder.status")
    print("SPPIDER: Start", file=open(temp_file, "a"))
    req = requests.post(
        url=url, data=content, headers={"Content-Type": header}, verify=False
    )
    temp_url = req.text.split('<a href="')[1].split('">')[0]
    result_url = wait_spider(temp_url, temp_file)

    pdb_url = ""

    time.sleep(10)

    r = requests.get(result_url)
    html = lxml.html.fromstring(r.text)
    refresh = html.cssselect('meta[http-equiv="Refresh"]')

    if not refresh:
        pass
    else:
        print("SPPIDER: URL {} refresh".format(temp_url), file=open(temp_file, "a"))
        x = refresh[0].attrib["content"].find("http")
        result_url = refresh[0].attrib["content"][x:]
        print("SPPIDER new URL {}".format(result_url), file=open(temp_file, "a"))

    for line in request.urlopen(result_url).readlines():
        if "sppider.pdb" in line.decode("utf-8"):
            print("SPPIDER: PDB url found", file=open(temp_file, "a"))
            line = line.decode("utf-8")
            pdb_url = line.split('<a href="')[1].split('"')[0]

    if pdb_url != "":
        results_pdb = pdb.from_url(
            pdb_url, name=f"{pdb_name}_SPPIDER", main_dir=main_dir
        )
        print("SPPIDER: Finished successfully", file=open(temp_file, "a"))
        return predictors.Predictor(pdb=results_pdb, name="SPPIDER", success=True)
    else:
        print("SPPIDER: Failed {}".format(result_url), file=open(temp_file, "a"))
        return predictors.Predictor(
            pdb=input_params.pdb_file, name="SPPIDER", success=False
        )
