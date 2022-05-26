"""CONS-PPISP module."""
import io
import logging
import re
import sys
import tempfile
import time

import mechanicalsoup as ms
import pandas as pd
import requests

from cport.modules.utils import get_pdb_from_pdbid
from cport.url import CONS_PPISP_URL

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 10  # seconds
# any request should never take more than 15min so theoretical max is 90 retries
NUM_RETRIES = 18


class ConsPPISP:
    """CONS-PPISP class."""

    def __init__(self, pdb_id, chain_id):
        """
        Initialize the class.

        Parameters
        ----------
        pdb_id : str
            Protein data bank identification code.
        chain_id : str
            Chain identifier.

        """
        self.pdb_id = pdb_id
        self.chain_id = chain_id
        self.wait = WAIT_INTERVAL
        self.tries = NUM_RETRIES

    def submit(self):
        """
        Make a submission to the cons-PPISP server.

        Returns
        -------
        processing_url : str
            The url to the processing page.

        """
        pdb_file = get_pdb_from_pdbid(self.pdb_id)

        # SSL request fails, try to find alternative solution as this
        #   would save a lot of code
        browser = ms.StatefulBrowser()
        browser.open(CONS_PPISP_URL, verify=False)

        input_form = browser.select_form(nr=0)
        input_form.set(name="submitter", value=str(self.pdb_id + self.chain_id))
        input_form.set(name="emailAddr", value="validmail@trustme.yes")
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
        """
        Retrieve the link to the result page.

        Parameters
        ----------
        url : str
            The url to the result results.
        page_text : str
            The text of the page to parse - used for testing.

        Returns
        -------
        url : str
            The url to the prediction page.

        """
        browser = ms.StatefulBrowser()

        if page_text:
            # this is used in the testing
            browser.open_fake_page(page_text=page_text)
            url = page_text
        else:
            browser.open(url, verify=False)

        completed = False
        while not completed:
            # Check if the result page exists
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
        """
        Download the results.

        Parameters
        ----------
        download_link : str
            The link to the results.

        Returns
        -------
        temp_file.name : str
            The path to the results file.

        """
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.name = requests.get(
            download_link, verify=False
        ).content  # needed a way to disable verification for SSL
        return temp_file.name

    def parse_prediction(self, url=None, test_file=None):
        """
        Take the results extracts the active and passive residue predictions.

        Parameters
        ----------
        url : str
            The url to the results.
        test_file : str
            The file to parse.

        Returns
        -------
        prediction_dict : dict
            The dictionary containing the parsed prediction results with active
            and passive sites.

        """
        prediction_dict = {"active": [], "passive": []}

        if test_file:
            final_predictions = pd.read_csv(
                test_file,
                skiprows=13,
                delim_whitespace=True,
                names=["AA", "Ch", "AA_nr", "Score", "Prediction"],
                header=0,
                skipfooter=16,
            )
        else:
            # direct reading of page with read_csv is impossible due to
            #  the same SSL error
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

    def run(self):
        """
        Execute the cons-PPISP prediction.

        Returns
        -------
        prediction_dict : dict
            A dictionary containing the raw prediction.

        """
        log.info("Running cons-PPISP")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        submitted_url = self.submit()
        prediction_url = self.retrieve_prediction_link(url=submitted_url)
        prediction_dict = self.parse_prediction(url=prediction_url)

        return prediction_dict
