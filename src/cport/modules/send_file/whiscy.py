import os
import time
from urllib import request

import lxml.html
import requests

from . import pdb, predictors

# from IPython import embed


def wait_whiscy(url, temp_file):
    waiting = 0
    while True:
        html_string = request.urlopen(url).read().decode("utf-8")
        if "404 Not Found" in html_string:
            raise AssertionError("Url not found")
        if waiting > 120 * 60:
            raise Exception("Timeout on the whiscy server")
        if "Status: Failed" in html_string:
            print_message = "Status Failed URL: {}".format(url)
            print(print_message, file=open(temp_file, "a"))
            return print_message
        if "[ERROR]" in html_string:
            error_message = html_string.split("[ERROR]")[1].split("<br/>")[0]
            print_message = "[Error] {} URL: {}".format(error_message, url)
            print(print_message, file=open(temp_file, "a"))
            return print_message
        if "whiscy.pdb" in html_string:
            for line in html_string.split(os.linesep):
                if "whiscy.pdb" in line:
                    pdb_dir = line
                    pdb_dir = pdb_dir.split('"')[-2]
                    pdb_url = "https://wenmr.science.uu.nl" + pdb_dir
                    print("WHISCY: URL found", file=open(temp_file, "a"))
                    return pdb_url
        else:
            print(
                "WHISCY: processing {} {}".format(waiting, url),
                file=open(temp_file, "a"),
            )
        time.sleep(5)
        waiting += 5


def get_csrf_token(page):
    html = lxml.html.fromstring(page)
    hidden_elements = html.xpath('//form//input[@type="hidden"]')
    token = {x.attrib["name"]: x.attrib["value"] for x in hidden_elements}
    return token["csrf_token"]


def run(input_params, main_dir, pdb_name):
    url = "https://wenmr.science.uu.nl/whiscy/"

    session = requests.session()
    init_session = session.get(url, verify=False)
    csrf_token = get_csrf_token(init_session.text)
    pdb_file = open(input_params.pdb_file.pdb_dir)
    seq_file = open(input_params.sequence_file.seq_dir)

    data = {
        "chain": input_params.chain_id,
        "alignment_format": input_params.sequence_file.format,
        "interface_propensities": True,
        "surface_smoothing": True,
        "csrf_token": csrf_token,
    }

    files = {"pdb_file": pdb_file, "alignment_file": seq_file}

    req = session.post(url=url, data=data, files=files)

    temp_dir = os.path.join(main_dir, "temp")
    temp_file = os.path.join(temp_dir, "whiscy.status")
    print("WHISCY: Start", file=open(temp_file, "a"))
    results_url = req.text.split('"')[-2]
    final_url = wait_whiscy(results_url, temp_file)

    if "Status Failed" in final_url:
        print("Status: Failed, rerun WHISCY", file=open(temp_file, "a"))
        new_session = requests.session()
        init_session = new_session.get(url, verify=False)
        csrf_token = get_csrf_token(init_session.text)
        pdb_file = open(input_params.pdb_file.pdb_dir)
        seq_file = open(input_params.sequence_file.seq_dir)

        data["csrf_token"] = csrf_token

        files = {"pdb_file": pdb_file, "alignment_file": seq_file}
        nreq = new_session.post(url=url, data=data, files=files)

        print("WHISCY: Restarting", file=open(temp_file, "a"))

        results_url = nreq.text.split('"')[-2]

        final_url = wait_whiscy(results_url, temp_file)
        if ("ERROR" in final_url) or ("Status: Failed" in final_url):
            print("WHISCY: Failed {}".format(final_url), file=open(temp_file, "a"))
            return predictors.Predictor(
                pdb=input_params.pdb_file, name="WHISCY", success=False
            )
        else:
            results_pdb = pdb.from_url(
                final_url, name=f"{pdb_name}_WHISCY", main_dir=main_dir
            )
            print("WHISCY: Run finished successfully", file=open(temp_file, "a"))
            return predictors.Predictor(pdb=results_pdb, name="WHISCY", success=True)
    elif "ERROR" in final_url:
        print("WHISCY: Failed {}".format(final_url), file=open(temp_file, "a"))
        return predictors.Predictor(
            pdb=input_params.pdb_file, name="WHISCY", success=False
        )
    else:
        results_pdb = pdb.from_url(
            final_url, name=f"{pdb_name}_WHISCY", main_dir=main_dir
        )
        print("WHISCY: Run finished successfully", file=open(temp_file, "a"))
        return predictors.Predictor(pdb=results_pdb, name="WHISCY", success=True)
