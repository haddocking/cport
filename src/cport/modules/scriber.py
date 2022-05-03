import time
import logging
import pandas as pd
import regex as re
import mechanicalsoup as ms
from urllib import request
from cport.url import SCRIBER_URL
import cport.modules.tools.pdb_fasta as pdb_fasta

log = logging.getLogger("cportlog")

class Scriber:
    def __init__(self, pdb_id, chain_id):
        self.pdb_id = pdb_id,
        self.chain_id = chain_id,
        self.prediction_dict = {"active": [], "passive": []}


    def run(self):
        mail_address = ""  # not as required as they make you believe

        # to allow for multiple requests, a list could be implemented as input, but server only allows for 10 at a time
        # so should split the list in subsets of 10 and check if the list is empty after every run, if not add new subset to queue

        error_msg = True

        fasta_string = pdb_fasta.get_pdb_fasta(self.pdb_id, self.chain_id)

        browser = ms.StatefulBrowser()
        browser.open(SCRIBER_URL)
        form_FASTA = browser.select_form(nr=0)
        form_FASTA.set(name="seq", value=fasta_string)
        form_FASTA.set(name="email1", value=mail_address)
        browser.submit_selected(btnName="Button1")

        # new page link to prevent resubmitting the same request
        links = browser.links()
        new_url = re.search(
            r"(http:.*)\"", str(links)
        )  # selects first link, which directs to result page
        log.info(
            "Run URL: " + new_url[1]
        )  # selects first match group, as the whole match contains a final " in the url
        browser.open(new_url[1])

        sleep = 0
        while (
            sleep < 600
        ):  # SCRIBER is rather fast so runs should take no longer than 10 minutes for single entries, re-evaluate for multiple requests
            if (
                re.search(r"(http:.*csv)", str(browser.page)) != None
            ):  # checks for the .csv download link, only present if the run is finished
                sleep = 700
                log.info(
                    "Results are ready"
                    )
                error_msg = False
            else:
                time.sleep(10)  # server only refreshes every 10 seconds
                sleep += 10
                log.info(
                    f"Waiting for {sleep} seconds"
                    )
                browser.refresh()  # without the refresh it does not detect the new .csv when its added

        if error_msg:
            log.info(
                "Suspected server time-out due to time it takes for results to be available"
                )

        download_link = re.search(r"(http:.*csv)", str(browser.page))[0]
        log.info(download_link)

        browser.close()

        # replace path to be functional on local machine
        # had to use request instead of mechanicalsoup due to link issues
        request.urlretrieve(
            url=download_link,
            filename="/Users/aldovandennieuwendijk/Documents/CPORT/test_output_requests/test_SCRIBER.csv",
        )
        
        final_predictions = pd.read_csv(
            "/Users/aldovandennieuwendijk/Documents/CPORT/test_output_requests/test_SCRIBER.csv",
            skiprows = 2,
            usecols=[0,1] # due to the structuring of the .csv file the header for these columns had to be skipped
            )


        for index, row in final_predictions.iterrows():
            if str.isupper(row["Unnamed: 1"]): # unnamed 1 holds the ResidueType, which is capitalized if it is a protein binding residue
                self.prediction_dict["active"].append(row["Unnamed: 0"]) # unnamed 0 holds the ResidueNumber, which is added to the correct list
            elif str.islower(row["Unnamed: 1"]):
                self.prediction_dict["passive"].append(row["Unnamed: 0"])
            else:
                log.info(
                    f"There appears that residue {row} is either empty or unprocessable"
                    )
        
        return self.prediction_dict
