import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from cport.url import PREDICTPROTEIN_URL
from cport.modules import utils

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 10  # seconds
NUM_RETRIES = 6


class Predictprotein:
    def __init__(self, pdb_id, chain_id):
        self.pdb_id = pdb_id
        self.chain_id = chain_id
        self.wait = WAIT_INTERVAL
        self.tries = NUM_RETRIES

    def submit(self):
        """Makes a submission to the PredictProtein server"""
        fasta_code = utils.get_fasta_from_pdbid(self.pdb_id, self.chain_id)

        """
        This is so far the only page which has javascript elements which
        have to be interacted with to submit the submission.
        This forces the use of selenium, as this is the only package capable
        of interacting with javascript on a page.
        Unsure of how viable this is to run on a server.
        Currently able to fill in the fasta_code and press the submit
        button, but following to the result page is still proving elusive.
        """

        driver = webdriver.Safari()
        driver.get(PREDICTPROTEIN_URL)

        # identifies the textarea
        elem = driver.find_element_by_id("sequence")
        elem.clear()
        elem.send_keys(fasta_code)

        # selects the specific button for submission
        driver.find_element_by_css_selector(
            "a.btn.btn-submit.btn-primary.btn-large"
        ).click()

        html = driver.page_source

        return html

    def run(self, test=False):
        """Execute the PredictProtein prediction."""
        log.info("Running PredictProtein")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        submitted_url = self.submit()
        # prediction_url = self.retrieve_prediction_link(url=submitted_url)
        # self.prediction_dict = self.parse_prediction(url=prediction_url)

        return submitted_url
