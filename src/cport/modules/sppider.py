"""SPPIDER module."""
import logging
import re
import sys
import time

import mechanicalsoup as ms

from cport.url import SPPIDER_URL

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 45  # seconds
# results take up to 5 minutes for 1ppe E, but are usually ready within 2 minutes
NUM_RETRIES = 36


class Sppider:
    """SPPIDER class."""

    def __init__(self, pdb_file, chain_id):
        """Initialize the SPPIDER class.

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
        Make a submission to the SPPIDER server.

        Returns
        -------
        submitted_url : str
            The url to the submitted page.

        """
        browser = ms.StatefulBrowser()
        browser.open(SPPIDER_URL)

        sppider_form = browser.select_form()
        with open(self.pdb_file, "rb") as file_obj:
            sppider_form.set(name="PDBFileName", value=file_obj)
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
        """
        Retrieve the link to the SPIDER prediction page.

        Parameters
        ----------
        url : str
            The url of the SPIDER processing page.
        page_text : str
            The text of the SPIDER processing page.

        Returns
        -------
        new_url : str
            The url of the prediction obtained SPIDER prediction page.

        """
        browser = ms.StatefulBrowser()

        if page_text:
            # this is used in the testing
            browser.open_fake_page(page_text=page_text)
        else:
            browser.open(url)

        completed = False
        while not completed:
            # if match is True, the results are not yet ready
            match = re.search(
                r"(Refresh page manually or it will be reloaded "
                r"automatically in 5 minutes)",
                str(browser.page),
            )
            if not match:
                completed = True
            else:
                # still running, wait a bit
                log.debug("Waiting for SPPIDER to finish... %s", self.tries)
                time.sleep(self.wait)
                browser.refresh()
                self.tries -= 1

            if self.tries == 0:
                # if tries is 0, then the server is not responding
                log.error("SPPIDER server is not responding, url was %s", url)
                sys.exit()

        # the page contains the correct link, which automatically opens in a browser
        #  soup browser is an exception so url needs to be extracted and opened
        #  to function
        # https://regex101.com/r/Izy7PR/1
        # print(str(browser.page))
        new_url = re.findall(r"URL=(.*?=int)", str(browser.page))[0]

        browser.close()

        return new_url

    @staticmethod
    def parse_prediction(url=None, page_text=None):
        """
        Take the results extracts the active and passive residue predictions.

        Parameters
        ----------
        url : str
            The url to the results.
        page_text : str
            The file to parse.

        Returns
        -------
        prediction_dict : dict
            The dictionary containing the parsed prediction results with active
            and passive sites.

        """
        # sppider only provides a list of active residues
        prediction_dict = {"active": [], "passive": []}
        prediction = {"active": []}
        browser = ms.StatefulBrowser()

        if page_text:
            # this is used in the testing
            browser.open_fake_page(page_text=page_text)
        else:
            browser.open(url)

        # https://regex101.com/r/iNn3FK/1 as an example, used DOTALL to include \n in
        #  results for flexibility
        page_search = re.findall(
            r"List of interacting residues predicted by SPPIDER:\n\(criteria"
            r" used: network majority count .*?= 5\)\n(.*?)\n\n",
            str(browser.page),
            re.DOTALL,
        )

        browser.close()

        # checks if any residues are actually predicted
        if page_search != ["None"]:
            # removes aa identifier to only retain the position of the residues
            active_list = re.sub(r"[A-Z]|\s", "", page_search[0])

            # splits on any non-word character, creating a list of all active residues
            prediction["active"] = re.split(r",", active_list)

            for item in prediction["active"]:
                prediction_dict["active"].append(int(item))
        """
        for i in range(1, 246):
            if i not in prediction_dict["active"]:
                prediction_dict["passive"].append(i)
        """
        return prediction_dict

    def run(self):
        """
        Execute the SPPIDER prediction.

        Returns
        -------
        prediction_dict : dict
            A dictionary containing the active and passive residue predictions.

        """
        log.info("Running SPPIDER")
        log.info(
            "Will try %s times waiting %ss between tries",
            self.tries,
            self.wait,
        )

        submitted_url = self.submit()
        prediction_url = self.retrieve_prediction_link(url=submitted_url)
        prediction_dict = self.parse_prediction(url=prediction_url)

        return prediction_dict
