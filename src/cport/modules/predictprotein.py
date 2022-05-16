import logging
import time
import sys
import os
import zipfile
import glob
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

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
        self.test_result_html = "https://predictprotein.org/visual_results?req_id=$1$0xeBp0R9$LnGQjDhYiCNTRQqkzios7/"
        self.test_path = (
            r"/Users/aldovandennieuwendijk/Documents/CPORT/test_output_requests/"
        )

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

        driver = webdriver.Chrome()
        driver.get(PREDICTPROTEIN_URL)

        # identifies the textarea
        elem = driver.find_element_by_id("sequence")
        elem.clear()
        elem.send_keys(fasta_code)

        # selects the specific button for submission
        driver.find_element_by_css_selector(
            "a.btn.btn-submit.btn-primary.btn-large"
        ).click()

        time.sleep(5)

        html = driver.current_url

        return html

    def retrieve_prediction_link(self, url=None):
        download_path = (
            r"/Users/aldovandennieuwendijk/Documents/CPORT/test_output_requests/"
        )
        options = Options()
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": download_path,
                "profile.default_content_setting_values.automatic_downloads": 2,
            },
        )
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(self.test_result_html)

        time.sleep(5)

        completed = False
        while not completed:
            # checks for the binding site button
            if driver.find_element_by_xpath('//*[@id="binding"]/a') != None:
                completed = True
            else:
                # still running, wait a bit
                log.debug(f"Waiting for Predict Protein to finish... {self.tries}")
                time.sleep(self.wait)
                driver.refresh()
                self.tries -= 1
            if self.tries == 0:
                # if tries is 0, then the server is not responding
                log.error(f"Predict Protein server is not responding, url was {url}")
                sys.exit()

        driver.find_element_by_xpath('//*[@id="binding"]/a').send_keys(Keys.ENTER)
        time.sleep(5)

        driver.find_element_by_xpath('//*[@id="Binding"]/div[2]/div/ul/li/a').send_keys(
            Keys.ENTER
        )
        time.sleep(5)

        driver.find_element_by_xpath(
            '//*[@id="Binding"]/div[2]/div/ul/li/ul/li[1]/a'
        ).click()
        time.sleep(5)

        return download_path

    def parse_prediction(self, path=None):
        prediction_dict = {"active": [], "passive": []}

        zip_file = glob.glob(f"{path}*.zip")[0]
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(path)

        os.remove(zip_file)

        final_predictions = pd.read_csv(
            f"{path}query.prona",
            skiprows=11,
            usecols=[0, 3],
            names=["Residue_Number", "Protein_Pred"],
            delim_whitespace=True,
        )

        for row in final_predictions.itertuples():
            if row.Protein_Pred == 1:  # uppercase denotes a predicted interaction
                prediction_dict["active"].append(row[0])
            elif row.Protein_Pred == 0:
                prediction_dict["passive"].append(row[0])
            else:
                log.warning(
                    f"There appears that residue {row} is either empty or unprocessable"
                )

        os.remove(f"{path}query.prona")

        return prediction_dict

    def run(self, test=False):
        """Execute the PredictProtein prediction."""
        log.info("Running PredictProtein")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        submitted_url = self.submit()
        result_path = self.retrieve_prediction_link(submitted_url)
        self.prediction_dict = self.parse_prediction(path=result_path)

        return self.prediction_dict
