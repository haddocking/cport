import logging
import re
import tempfile
import time
import sys

import mechanicalsoup as ms
from cport.url import SPPIDER_URL

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 10  # seconds
NUM_RETRIES = 12  # results take up to 5 minutes for 1ppe E, but are usually ready within 2 minutes


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

        submitted_url = browser.url

        if not submitted_url:
            log.error("SPPIDER submission failed")
            sys.exit()

        browser.close()

        return submitted_url

    def retrieve_prediction_link(self, url=None, page_text=None):
        browser = ms.StatefulBrowser()

        if page_text:
            # this is used in the testing
            browser.open_fake_page(page_text=page_text)
        else:
            browser.open(url)

        log.info(f"Request url is {url}")
        completed = False
        while not completed:
            # if match is True, the results are not yet ready
            match = re.search(
                r"(Refresh page manually or it will be reloaded automatically in 5 minutes)",
                str(browser.page),
            )
            if not match:
                completed = True
            else:
                # still running, wait a bit
                log.debug(f"Waiting for SPPIDER to finish... {self.tries}")
                time.sleep(self.wait)
                browser.refresh()
                self.tries -= 1

            if self.tries == 0:
                # if tries is 0, then the server is not responding
                log.error(f"SPPIDER server is not responding, url was {url}")
                sys.exit()

        # the page contains the correct link, which automatically opens in a browser
        # soup browser is an exception so url needs to be extracted and opened to function
        new_url = re.findall(r"URL=(.*?=int)", str(browser.page))

        browser.close()

        return new_url[0]

    def parse_prediction(self, url=None, page_text=None):
        prediction_dict = {
            "active": [],
            "passive": [],
        }  # sppider only provides a list of active residues
        browser = ms.StatefulBrowser()

        if page_text:
            # this is used in the testing
            browser.open_fake_page(page_text=page_text)
        else:
            browser.open(url)

        # https://regex101.com/r/iNn3FK/1 as an example, used DOTALL to include \n in results for flexibility
        page_search = re.findall(
            r"List of interacting residues predicted by SPPIDER:\n\(criteria used: network majority count .*?= 5\)\n(.*?)\n\n",
            str(browser.page),
            re.DOTALL,
        )

        browser.close()

        # removes aa identifier to only retain the position of the residues
        active_list = re.sub(r"[A-Z]", "", page_search[0])

        # splits on any non-word character, creating a list of all active residues
        prediction_dict["active"] = re.split(r"\W+", active_list)

        return prediction_dict

    def run(self, test=False):
        """Execute the SPPIDER prediction."""
        log.info("Running SPPIDER")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        submitted_url = self.submit()
        prediction_url = self.retrieve_prediction_link(url=submitted_url)
        self.prediction_dict = self.parse_prediction(url=prediction_url)

        return self.prediction_dict
