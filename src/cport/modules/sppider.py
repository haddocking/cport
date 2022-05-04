import logging
import re
import tempfile
import time
import sys
from urllib import request

import pandas as pd

import mechanicalsoup as ms
from cport.url import SPPIDER_URL

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 10  # seconds
NUM_RETRIES = 6

class Sppider:
    def __init__(self, pdb_id, chain_id):
        self.pdb_id = pdb_id
        self.chain_id = chain_id
        self.wait = WAIT_INTERVAL
        self.tries = NUM_RETRIES
    
    def submit(self):
        browser = ms.StatefulBrowser()
        browser.open(SPPIDER_URL)

        sppider_form = browser.select_form()
        sppider_form.set(name="PDBCode", value=self.pdb_id)
        sppider_form.set(name="PDBChain", value=self.chain_id)
        
        browser.submit_selected()

        sppider_links = browser.links()
        browser.follow_link(sppider_links[0])

        browser.launch_browser()
        submission_url = browser.url


        if not submission_url:
            log.error("SPPIDER submission failed")
            sys.exit()

        browser.close()

        return submission_url


    def run(self, test=False):
        """Execute the SPPIDER prediction."""
        log.info("Running SPPIDER")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        submitted_url = self.submit()
       # prediction_link = self.retrieve_prediction_link(url=submitted_url)
       # result_file = self.download_result(prediction_link)
       # self.prediction_dict = self.parse_prediction(result_file)

        return submitted_url