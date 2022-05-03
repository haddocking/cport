import time
import re
import logging
import mechanicalsoup as ms
from cport.url import WHISCY_URL


log = logging.getLogger("cportlog")


class Whiscy:
    def __init__(self, pdb_id, chain_id):
        self.pdb_id = pdb_id
        self.chain_id = chain_id
        self.prediction_dict = {"active": [], "passive": []}

    def run(self):
        """Run the prediction."""
        # replace with input
        # url = "https://wenmr.science.uu.nl/whiscy/"
        # pdb_name = "1PPE"
        # chain_id = "E"
        # align_type = "FASTA"
        browser = ms.StatefulBrowser()
        browser.open(WHISCY_URL)

        form = browser.select_form(nr=1)
        form.set(name="pdb_id", value=self.pdb_id)
        form.set(name="chain", value=self.chain_id.capitalize())
        form.set(name="hssp_id", value=self.pdb_id)
        form.set(name="alignment_format", value="FASTA")

        browser.submit_selected(btnName="submit")

        page_text = browser.page
        page_text_list = str(page_text.find_all("p"))

        # https://regex101.com/r/rwcIl8/1
        new_url = re.findall(r"(https:.*)\"", page_text_list)[0]
        log.info(f"Run URL: {new_url}")
        browser.open(new_url)

        error_msg = True
        sleep = 0
        while sleep < 600:
            if browser.page.find_all(id="active_list"):
                sleep = 700
                log.info("Results are ready")
                error_msg = False
            else:
                time.sleep(5)
                sleep += 5
                log.info(f"Waiting for {sleep} seconds")
                browser.refresh()

        if (
            error_msg
        ):  # if program gets here without having disabled error_msg something is likely wrong
            log.info(
                "Suspected server time-out due to time it takes for results to be available"
            )

        active_residues = browser.page.find_all(id="active_list")
        passive_residues = browser.page.find_all(id="passive_list")

        browser.close()

        # takes just the residue lists from the page and splits them into lists
        active_residues_list = re.split(
            r"\,", re.search(r"\">(.*)</", str(active_residues))[1]
        )
        passive_residues_list = re.split(
            r"\,", re.search(r"\">(.*)</", str(passive_residues))[1]
        )

        # residues_list are strings, make them into integers
        self.prediction_dict["active"] = list(map(int, active_residues_list))
        self.prediction_dict["passive"] = list(map(int, passive_residues_list))

        return self.prediction_dict
