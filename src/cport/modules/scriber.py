import logging
import re
import tempfile
import time
import sys
from urllib import request

import pandas as pd

import mechanicalsoup as ms
from cport.modules.utils import get_fasta_from_pdbid
from cport.url import SCRIBER_URL

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 10  # seconds
NUM_RETRIES = 6


class Scriber:
    def __init__(self, pdb_id, chain_id):
        self.pdb_id = pdb_id
        self.chain_id = chain_id
        self.wait = WAIT_INTERVAL
        self.tries = NUM_RETRIES

    def submit(self):
        """Make a submission to Scriber."""
        fasta_string = get_fasta_from_pdbid(self.pdb_id, self.chain_id)

        browser = ms.StatefulBrowser()

        browser.open(SCRIBER_URL)

        form_FASTA = browser.select_form(nr=0)
        form_FASTA.set(name="seq", value=fasta_string)
        form_FASTA.set(name="email1", value="")
        browser.submit_selected(btnName="Button1")
        links = browser.links()

        browser.close()

        submitted_url = re.findall(r"(http:.*)\"", str(links))[0]
        if not submitted_url:
            log.error("SCRIBE submission failed")
            sys.exit()

        return submitted_url

    def retrieve_prediction_link(self, url=None, page_text=None):
        """Retrieve the results."""
        browser = ms.StatefulBrowser()

        if page_text:
            # this is used in the testing
            browser.open_fake_page(page_text=page_text)
        else:
            browser.open(url)

        completed = False
        while not completed:
            # Check if there's a .csv file in the page
            match = re.search(r"(http:.*csv)", str(browser.page))
            if match:
                completed = True
            else:
                # still running, wait a bit
                log.debug(f"Waiting for SCRIBER to finish... {self.tries}")
                time.sleep(self.wait)
                browser.refresh()
                self.tries -= 1

            if self.tries == 0:
                # if tries is 0, then the server is not responding
                log.error(f"SCRIBER server is not responding, url was {url}")
                sys.exit()

        result_csv_link = re.search(r"(http:.*csv)", str(browser.page))[0]

        browser.close()

        return result_csv_link

    @staticmethod
    def download_result(download_link):
        """Download the results."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        request.urlretrieve(download_link, temp_file.name)
        return temp_file.name

    @staticmethod
    def parse_prediction(result_file):
        """Parse the Scriber prediction."""
        prediction_dict = {"active": [], "passive": []}

        # Read back the .csv file and store it in a pandas dataframe
        #  due to the structuring of the .csv file the header for these columns had to be skipped
        final_predictions = pd.read_csv(
            result_file,
            skiprows=2,
            usecols=[
                0,
                1,
            ],
        )

        # manually added header names back
        final_predictions.columns = [
            "ResidueNumber",
            "ResidueType",
        ]

        for row in final_predictions.itertuples():
            if str.isupper(
                row.ResidueType
            ):  # uppercase denotes a predicted interaction
                prediction_dict["active"].append(row.ResidueNumber)
            elif str.islower(row.ResidueType):
                prediction_dict["passive"].append(row.ResidueNumber)
            else:
                log.warning(
                    f"There appears that residue {row} is either empty or unprocessable"
                )

        return prediction_dict

    def run(self, test=False):
        """Execute the Scriber prediction."""
        log.info("Running SCRIBER")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        submitted_url = self.submit()
        prediction_link = self.retrieve_prediction_link(url=submitted_url)
        result_file = self.download_result(prediction_link)
        self.prediction_dict = self.parse_prediction(result_file)

        return self.prediction_dict
