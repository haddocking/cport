"""Whiscy module."""
import logging
import os
import re
import shutil
import sys
import time

import mechanicalsoup as ms

from cport.url import WHISCY_URL

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 10  # seconds
NUM_RETRIES = 6


class Whiscy:
    """Whiscy class."""

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
        Make a submission to WHISCY.

        Returns
        -------
        new_url : str
            The url to the processing page.

        """
        # take the exact name of the pdb input without the entire path
        filename = str(self.pdb_file)[-8:]
        # A temporary file needs to be created to avoid WHISCY renaming the input
        # to the entire path name causing the prediction to not run as the name
        # of the input needs to match the hssp name otherwise it will not match
        # A more elegant workaround would be preferable, but eludes me as of yet
        shutil.copyfile(self.pdb_file, filename)

        browser = ms.StatefulBrowser()
        browser.open(WHISCY_URL)

        form = browser.select_form(nr=1)
        form.set(name="pdb_file", value=filename)
        form.set(name="chain", value=self.chain_id.capitalize())
        form.set(name="hssp_id", value=str(self.pdb_file)[-8:-4])
        form.set(name="alignment_format", value="FASTA")

        browser.submit_selected(btnName="submit")

        page_text = browser.page
        page_text_list = str(page_text.find_all("p"))

        # https://regex101.com/r/rwcIl8/1
        new_url = re.findall(r"(https:.*)\"", page_text_list)[0]

        browser.close()
        # remove file in main directory for cleanliness
        os.unlink(filename)

        return new_url

    def retrieve_prediction(self, url=None, page_text=None):
        """Retrieve the results.

        Parameters
        ----------
        url : str
            The url to the results.
        page_text : str
            The text of the page to parse - used for testing.

        Returns
        -------
        prediction_dict : dict
            The dictionary containing the parsed prediction results with active
            and passive sites.

        """
        prediction_dict = {"active": [], "passive": []}
        browser = ms.StatefulBrowser()

        if page_text:
            # this is used in the testing
            browser.open_fake_page(page_text=page_text)
        else:
            browser.open(url)

        completed = False
        while not completed:
            # Check if there's a list of active reisued in the page
            if browser.page.find_all(id="active_list"):
                completed = True
            else:
                # still running, wait a bit
                log.debug("Waiting for WHISCY to finish... %s", self.tries)
                time.sleep(self.wait)
                browser.refresh()
                self.tries -= 1

            if self.tries == 0:
                # if tries is 0, then the server is not responding
                log.error("WHISCY server is not responding, url was %s", url)
                sys.exit()

        active_residues_list = re.split(
            r"\,",
            re.search(r"\">(.*)</", str(browser.page.find_all(id="active_list")))[1],
        )
        passive_residues_list = re.split(
            r"\,",
            re.search(r"\">(.*)</", str(browser.page.find_all(id="passive_list")))[1],
        )

        prediction_dict["active"] = list(map(int, active_residues_list))
        prediction_dict["passive"] = list(map(int, passive_residues_list))

        browser.close()

        return prediction_dict

    def run(self):
        """
        Run the whiscy predictor.

        Returns
        -------
        prediction_dict : dict
            A dictionary containing the raw prediction.

        """
        submitted_url = self.submit()
        prediction_dict = self.retrieve_prediction(url=submitted_url)

        return prediction_dict
