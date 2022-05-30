"""PSIVER module."""
import gzip
import logging
import re
import sys
import tempfile
import time
from io import StringIO

import mechanicalsoup as ms
import pandas as pd
import requests

from cport.modules.utils import get_fasta_from_pdbid
from cport.url import PSIVER_URL

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 10  # seconds
NUM_RETRIES = 6


class Psiver:
    """PSIVER class."""

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
        self.test_url = (
            "https://mizuguchilab.org/PSIVER/users_cache/example/psiver_result.html"
        )

    def submit(self):
        """
        Make a submission to the PSIVER server.

        Returns
        -------
        submission_link: str
            url resulting from submission.
        """
        sequence = get_fasta_from_pdbid(self.pdb_id, self.chain_id)
        # FASTA header must be removed from sequence
        sequence_headless = "".join(sequence.splitlines(keepends=True)[1:])

        browser = ms.StatefulBrowser()
        browser.open(PSIVER_URL)

        input_form = browser.select_form(nr=0)
        input_form.set_textarea({"fasta_seq": sequence_headless})
        browser.submit_selected()

        wait_page = str(browser.page)
        # https://regex101.com/r/Mo8rwL/1
        wait_link = re.findall(r"href=\"(.*)\"</script", wait_page)[0]

        return wait_link

    def retrieve_prediction_link(self, url=None, page_text=None):
        """
        Retrieve the link to the meta-PPISP prediction page.

        Parameters
        ----------
        url : str
            The url of the meta-PPISP processing page.
        page_text : str
            The text of the meta-PPISP processing page.

        Returns
        -------
        url : str
            The url of the obtained meta-PPISP prediction page.

        """

        browser = ms.StatefulBrowser()

        if page_text:
            # this is used in the testing
            browser.open_fake_page(page_text=page_text)
            url = page_text
        else:
            browser.open(url)

        completed = False
        while not completed:
            # Check if the result page exists
            # https://regex101.com/r/MzRYcb/1
            match = re.search(r"<title>psiver results</title>", str(browser.page))
            if match:
                completed = True
            else:
                # still running, wait a bit
                log.debug(f"Waiting for PSIVER to finish... {self.tries}")
                time.sleep(self.wait)
                browser.refresh()
                self.tries -= 1

            if self.tries == 0:
                # if tries is 0, then the server is not responding
                log.error(f"PSIVER server is not responding, url was {url}")
                sys.exit()

        download_link = browser.links()[1]
        browser.follow_link(download_link)

        return browser.url

    @staticmethod
    def download_result(download_link):
        """
        Download the results.

        Parameters
        ----------
        download_link : str
            The url of the meta-PPISP result page.

        Returns
        -------
        temp_file.name : str
            The name of the temporary file containing the results.

        """
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(requests.get(download_link).content)
        return temp_file.name

    def parse_prediction(self, pred_url=None, test_file=None):
        """
        Take the results extracts the active and passive residue predictions.

        Parameters
        ----------
        pred_url : str
            The url of the PSIVER result page.
        test_file : str
            A file containing the text present in the result page

        Returns
        -------
        prediction_dict : dict
            A dictionary containing the active and passive residue predictions.

        """
        prediction_dict = {"active": [], "passive": []}

        if test_file:
            # for testing purposes
            result_file = test_file
        else:
            download_file = self.download_result(pred_url)
            with gzip.open(download_file, "rt") as f:
                file_content = f.read()
            result_file = StringIO(file_content)

        final_predictions = pd.read_csv(
            result_file,
            header=0,
            skiprows=15,
            usecols=[1, 2, 4],
            names=["residue", "prediction", "score"],
            delim_whitespace=True,
            skipfooter=12,
        )

        for row in final_predictions.itertuples():
            # 1 indicates interaction
            if row.prediction == "-":
                interaction = False
            else:
                interaction = True
                # adds standardized score to positive residues
                score = row.score

            residue_number = row.residue
            if interaction:
                prediction_dict["active"].append([residue_number, score])
            elif not interaction:
                prediction_dict["passive"].append(residue_number)
            else:
                log.warning(
                    f"There appears that residue {row} is either empty or unprocessable"
                )

        return prediction_dict

    def run(self):
        """
        Execute the PSIVER prediction.

        Returns
        -------
        prediction_dict : dict
            A dictionary containing the active and passive residue predictions.

        """
        log.info("Running PSIVER")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        # submitted_url = self.submit()
        prediction_url = self.retrieve_prediction_link(url=self.test_url)
        prediction_dict = self.parse_prediction(pred_url=prediction_url)

        return prediction_dict
