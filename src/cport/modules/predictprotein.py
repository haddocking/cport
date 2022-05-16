import logging
import time
import sys
import os
import zipfile
import glob
import pandas as pd
import tempfile
import shutil

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

        # sleep so that the page is properly loaded before continuing
        time.sleep(5)

        html = driver.current_url

        return html

    def retrieve_prediction_link(self, url=None):
        temp_dir = tempfile.mkdtemp()
        options = Options()
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": temp_dir,
                "profile.default_content_setting_values.automatic_downloads": 2,
            },
        )
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)

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

        # finds buttons / elements by xpath
        driver.find_element_by_xpath('//*[@id="binding"]/a').send_keys(Keys.ENTER)
        # sleep to allow the next page to load as to avoid buttons not being seen
        time.sleep(5)

        driver.find_element_by_xpath('//*[@id="Binding"]/div[2]/div/ul/li/a').send_keys(
            Keys.ENTER
        )
        time.sleep(5)

        driver.find_element_by_xpath(
            '//*[@id="Binding"]/div[2]/div/ul/li/ul/li[1]/a'
        ).click()
        time.sleep(5)

        return temp_dir

    def parse_prediction(self, dir=None):
        prediction_dict = {"active": [], "passive": []}

        # returns a list of all zip files, will only be 1
        zip_file = glob.glob(f"{dir}/*.zip")[0]
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(f"{dir}/")

        os.remove(zip_file)

        result_file = glob.glob(f"{dir}/*.prona")[0]

        final_predictions = pd.read_csv(
            result_file,
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

        os.remove(f"{dir}/query.prona")
        shutil.rmtree(dir)

        return prediction_dict

    def run(self, test=False):
        """Execute the PredictProtein prediction."""
        log.info("Running PredictProtein")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        submitted_url = self.submit()
        temp_dir = self.retrieve_prediction_link(submitted_url)
        self.prediction_dict = self.parse_prediction(dir=temp_dir)

        return self.prediction_dict
