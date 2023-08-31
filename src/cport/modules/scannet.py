"""ScanNet module."""
import io
import logging
import re
import sys
import time
import warnings

import mechanicalsoup as ms
from Bio import PDB, BiopythonWarning

with warnings.catch_warnings():
    warnings.simplefilter("ignore", BiopythonWarning)

from cport.url import SCANNET_URL

log = logging.getLogger("cportlog")
result_url = "http://bioinfo3d.cs.tau.ac.il/ScanNet/results/0407500892.html"

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 30  # seconds
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
        input_form.set(name="email", value="validmail@trustme.yes")
        input_form.set(name="chain", value=self.chain_id)
        with open(self.pdb_file, "rb") as file_obj:
            input_form.set(name="PDBfile", value=file_obj)
            browser.submit_selected()

        browser.follow_link(browser.links()[7])
        processing_url = browser.get_url()
        log.debug(f"The url being looked at: {processing_url}")
        print(processing_url)
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
            # Check if the variable with the results is present
            match = re.search(r"stringContainingTheWholePdbFile", str(browser.page))
            if match:
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
        parser = PDB.PDBParser()
        if not test_file:
            browser = ms.StatefulBrowser()

            browser.open(url)
            # page contains PDB file as a string with results in b_factor column
            pdb_string = re.findall(
                r"stringContainingTheWholePdbFile = `(.*?)`",
                str(browser.page),
                re.DOTALL,
            )
            # print(pdb_string)
            # print(pdb_string[0])
            structure = parser.get_structure("pdb", io.StringIO(pdb_string[0]))

        else:
            structure = parser.get_structure("pdb", test_file)
        print()
        print(structure[0])
        print()
        model = structure[0]
        chain = model[self.chain_id]

        prediction_dict = {"active": [], "passive": []}

        for res in chain:
            for atom in res:
                b_fact = atom.get_bfactor()

            # arbitrary value for active
            if b_fact >= 0.5:
                prediction_dict["active"].append([res.id[1], b_fact])
            else:
                prediction_dict["passive"].append([res.id[1], b_fact])

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

        submitted_url = self.submit()
        prediction_url = self.retrieve_prediction_link(url=submitted_url)
        prediction_dict = self.parse_prediction(url=prediction_url)

        return prediction_dict
