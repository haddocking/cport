import logging
import re
import sys
import tempfile
import time
from urllib import request

import mechanicalsoup as ms
import pandas as pd

from cport.modules.utils import get_pdb_from_pdbid
from cport.url import ISPRED4_URL

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 10  # seconds
NUM_RETRIES = 6


class Ispred4:
    def __init__(self, pdb_id, chain_id):
        self.pdb_id = pdb_id
        self.chain_id = chain_id
        self.wait = WAIT_INTERVAL
        self.tries = NUM_RETRIES

    def submit(self):
        pdb_file = get_pdb_from_pdbid(self.pdb_id)

        browser = ms.StatefulBrowser()
        browser.open(ISPRED4_URL)

        input_form = browser.select_form(nr=0)
        input_form.set(name="structure", value=pdb_file)
        input_form.set(name="ispred_chain", value=self.chain_id)
        input_form.set(
            name="ispred_rsath", value="0.20"
        )  # this is the default value, could be changed for analysis later
        browser.submit_selected()

        # https://regex101.com/r/KFLLil/1
        job_id = re.findall(r"Jobid:.*?;\">(.*?)</div>", str(browser.page))[0]

        if not job_id:
            log.error("ISPRED4 submission failed")
            sys.exit()

        browser.close()

        # once the job_id is available for a successfull submission, it can be used for future urls
        summary_url = f"{ISPRED4_URL}job_summary?jobid={job_id}"

        return summary_url

    def retrieve_prediction_link(self, url=None, page_text=None):
        """Retrieve the results."""
        browser = ms.StatefulBrowser()

        if page_text:
            # this is used in the testing
            browser.open_fake_page(page_text=page_text)
            # https://regex101.com/r/ulO1lf/1
            job_id = re.findall(r"id=(.*)", str(page_text))[0]
        else:
            browser.open(url)
            # https://regex101.com/r/ulO1lf/1
            job_id = re.findall(r"id=(.*)", str(url))[0]

        completed = False
        while not completed:
            # Check if the completion time has replaced the placeholder string
            # https://regex101.com/r/fK3U6b/1
            match = re.findall(r">--<", str(browser.page))
            if not match:
                completed = True
            else:
                # still running, wait a bit
                log.debug(f"Waiting for ISPRED4 to finish... {self.tries}")
                time.sleep(self.wait)
                browser.open(url)
                self.tries -= 1

            if self.tries == 0:
                # if tries is 0, then the server is not responding
                log.error(f"ISPRED4 server is not responding, url was {url}")
                sys.exit()

        download_url = f"{ISPRED4_URL}downloadjob?jobid={job_id}"

        return download_url

    @staticmethod
    def download_result(download_link):
        """Download the results."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        request.urlretrieve(download_link, temp_file.name)
        return temp_file.name

    @staticmethod
    def parse_prediction(result_file):
        """Parse the ISPRED4 prediction."""
        prediction_dict = {"active": [], "passive": []}

        # textfile with whitespaces as delimiter
        final_predictions = pd.read_csv(result_file, skiprows=15, delim_whitespace=True)

        # only surface residues have a yes or no in the Inter column, all skipped residues are buried
        for row in final_predictions.itertuples():
            if row.Inter == "yes":  # indicates high likelihood of interaction
                prediction_dict["active"].append(row.ResNum)
            elif row.Inter == "no":
                prediction_dict["passive"].append(row.ResNum)

        return prediction_dict

    def run(self, test=False):
        """Execute the ISPRED4 prediction."""
        log.info("Running ISPRED4")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        submitted_url = self.submit()
        prediction_link = self.retrieve_prediction_link(url=submitted_url)
        result_file = self.download_result(prediction_link)
        self.prediction_dict = self.parse_prediction(result_file)

        return self.prediction_dict
