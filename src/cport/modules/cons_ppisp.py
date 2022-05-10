import logging
import re
import time
import sys
import requests
import tempfile
import io

import mechanicalsoup as ms
import pandas as pd

from cport.url import CONS_PPISP_URL
from cport.modules.utils import get_pdb_from_pdbid

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 10  # seconds
NUM_RETRIES = 18


class Cons_ppisp:
    def __init__(self, pdb_id, chain_id):
        self.pdb_id = pdb_id
        self.chain_id = chain_id
        self.wait = WAIT_INTERVAL
        self.tries = NUM_RETRIES
        self.test_url = "https://pipe.rcc.fsu.edu/showresults/mail.message.040000240"

    def submit(self):
        pdb_file = get_pdb_from_pdbid(self.pdb_id)

        browser = ms.StatefulBrowser()
        browser.open(
            CONS_PPISP_URL, verify=False
        )  # SSL request fails, try to find alternative solution

        input_form = browser.select_form(nr=0)
        input_form.set(name="submitter", value=str(self.pdb_id + self.chain_id))
        input_form.set(name="emailAddr", value="royaj88419@bunlets.com")
        input_form.set(name="pChain", value=self.chain_id)
        input_form.set(name="userfile", value=pdb_file)
        browser.submit_selected()

        # https://regex101.com/r/FBgZFE/1
        processing_url = re.findall(r"<a href=\"(.*)\">this link<", str(browser.page))[
            0
        ]
        log.debug(f"The url being looked at: {processing_url}")

        return processing_url

    def retrieve_prediction_link(self, url=None, page_text=None):
        browser = ms.StatefulBrowser()

        if page_text:
            # this is used in the testing
            browser.open_fake_page(page_text=page_text)
        else:
            browser.open(url, verify=False)

        completed = False
        while not completed:
            # Check if there is a link to the result page
            # https://regex101.com/r/8am6cs/1
            match = re.search(r"404 Not Found", str(browser.page))
            if not match:
                completed = True
            else:
                # still running, wait a bit
                log.debug(f"Waiting for cons-PPISP to finish... {self.tries}")
                time.sleep(self.wait)
                browser.refresh()
                self.tries -= 1

            if self.tries == 0:
                # if tries is 0, then the server is not responding
                log.error(f"cons-PPISP server is not responding, url was {url}")
                sys.exit()

        return url

    @staticmethod
    def download_result(download_link):
        """Download the results."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.name = requests.get(download_link, verify=False).content
        return temp_file.name

    def parse_prediction(self, url=None):
        prediction_dict = {"active": [], "passive": []}

        file = self.download_result(url)
        final_predictions = pd.read_csv(
            io.StringIO(file.decode("utf-8")),
            skiprows=13,
            delim_whitespace=True,
            names=["AA", "Ch", "AA_nr", "Score", "Prediction"],
            header=0,
            skipfooter=16,
        )

        for row in final_predictions.itertuples():
            if row.Prediction == "P":  # positive for interaction
                prediction_dict["active"].append(row.AA_nr)
            elif row.Prediction == "N":
                prediction_dict["passive"].append(row.AA_nr)

        return prediction_dict

    def run(self, test=False):
        """Execute the cons-PPISP prediction."""
        log.info("Running cons-PPISP")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        submitted_url = self.submit()
        prediction_url = self.retrieve_prediction_link(url=submitted_url)
        self.prediction_dict = self.parse_prediction(url=prediction_url)

        return self.prediction_dict
