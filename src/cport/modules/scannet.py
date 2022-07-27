"""ScanNet module."""
import io
import logging
import re
import sys
import tempfile
import time

import mechanicalsoup as ms
import pandas as pd
import requests

from cport.url import SCANNET_URL

log = logging.getLogger("cportlog")
result_url = "http://bioinfo3d.cs.tau.ac.il/ScanNet/results/0407500892.html"

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 30  # seconds
# any request should never take more than 15min so theoretical max is 90 retries
NUM_RETRIES = 36


class ScanNet:
    """ScanNet class."""

    def __init__(self, pdb_file, chain_id):
        """
        Initialize the class.

        Parameters
        ----------
        pdb_file : str
            Path to PDB file.
        chain_id : str
            Chain identifier.

        """
        self.pdb_file = pdb_file
        self.chain_id = chain_id
        self.wait = WAIT_INTERVAL
        self.tries = NUM_RETRIES

    def submit(self):
        """
        Make a submission to the ScanNet server.

        Returns
        -------
        processing_url : str
            The url to the processing page.

        """
        browser = ms.StatefulBrowser()
        browser.open(SCANNET_URL, verify=False)

        input_form = browser.select_form(nr=0)
        input_form.set(name="PDBfile", value=self.pdb_file)
        input_form.set(name="email", value="validmail@trustme.yes")
        input_form.set(name="chain", value=self.chain_id)
        browser.submit_selected()

        processing_url = browser.links()[7]
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
                log.debug(f"Waiting for ScanNet to finish... {self.tries}")
                time.sleep(self.wait)
                browser.refresh()
                self.tries -= 1

            if self.tries == 0:
                # if tries is 0, then the server is not responding
                log.error(f"ScanNet server is not responding, url was {url}")
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
        # this verify=False is a security issue but i'm afraid there's
        #  no trivial solution and that the issue might be of the server
        temp_file.name = requests.get(download_link, verify=False).content  # nosec
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
                error_bad_lines=False,
            )

        for row in final_predictions.itertuples():
            if row.Prediction == "P":  # positive for interaction
                # cons_ppisp occasionally adds an A to the number, needs to be removed
                prediction_dict["active"].append(
                    # trunk-ignore(flake8/W605)
                    [int(re.sub("\D", "", row.AA_nr)), row.Score]
                )
            elif row.Prediction == "N":
                # trunk-ignore(flake8/W605)
                prediction_dict["passive"].append(int(re.sub("\D", "", row.AA_nr)))

        return prediction_dict

    def run(self):
        """
        Execute the ScanNet prediction.

        Returns
        -------
        prediction_dict : dict
            A dictionary containing the raw prediction.

        """
        log.info("Running ScanNet")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        # submitted_url = self.submit()
        prediction_url = self.retrieve_prediction_link(url=submitted_url)
        prediction_dict = self.parse_prediction(url=prediction_url)

        return prediction_dict
