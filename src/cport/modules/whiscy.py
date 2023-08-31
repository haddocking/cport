"""Whiscy module."""
import logging
import os
import re
import shutil
import sys
import time
import warnings
from pathlib import Path

import mechanicalsoup as ms
from Bio import AlignIO, BiopythonWarning
from Bio.Blast import NCBIWWW
from defusedxml import lxml as ET

with warnings.catch_warnings():
    warnings.simplefilter("ignore", BiopythonWarning)

from cport.modules.utils import get_fasta_from_pdbfile
from cport.url import WHISCY_URL

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 10  # seconds
NUM_RETRIES = 24


class Whiscy:
    """Whiscy class."""

    def __init__(self, pdb_file, chain_id):
        """
        Initialize the class.

        Parameters
        ----------
        pdb_file : str or PosixPath
            Path to PDB file.
        chain_id : str
            Chain identifier.

        """
        self.pdb_file = Path(pdb_file)
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
        # A temporary file needs to be created to avoid WHISCY renaming the input
        # to the entire path name causing the prediction to not run as the name
        # of the input needs to match the hssp name otherwise it will not match
        # A more elegant workaround would be preferable, but eludes me as of yet
        filename = Path(f"{self.pdb_file.stem}_whiscy.pdb")
        shutil.copyfile(self.pdb_file, filename)

        blast_seq = get_fasta_from_pdbfile(self.pdb_file, self.chain_id)
        blast_len = len(blast_seq)
        log.debug("Running BLAST")
        blast_res_handle = NCBIWWW.qblast("blastp", "nr", blast_seq, hitlist_size=50)
        # This is the only somewhat realistic implementation without writing a whole
        # program from scratch to get BLAST or downloading an excessive amount of
        # FASTA aa sequence files.
        # The downside is that this does not provide a proper alignment file that
        # can be used by WHISCY, so this has to be done manually

        log.debug("Finished BLAST")
        with open("blast_res.xml", "w") as save_output:
            blast_res = blast_res_handle.read()
            save_output.write(blast_res)

        align_string = ">main\n" + blast_seq + "\n"
        tree = ET.parse("blast_res.xml")
        root = tree.getroot()
        for hit in root[8][0][4]:
            align_len = hit[5][0][13].text
            # workaround to make sure sequences are the same length for alignment
            if int(align_len) == blast_len:
                aa_string = hit[5][0][16].text
                # [5][0][16] for sequence, [1] for hit_id
                align_string += (
                    ">" + hit[1].text + "\n" + aa_string.replace(" ", "-") + "\n"
                )
            else:
                continue

        log.debug("Preparing alignment for WHISCY")
        with open("temp_align.fasta", "w") as temp_align:
            temp_align.write(align_string)

        # prepares proper alignment file for WHISCY
        alignment = AlignIO.read("temp_align.fasta", "fasta")

        with open("align.fasta", "w") as align:
            align.write(format(alignment, "fasta"))

        browser = ms.StatefulBrowser()

        browser.open(WHISCY_URL)

        form = browser.select_form(nr=1)
        form.set(name="pdb_file", value=filename)
        form.set(name="chain", value=self.chain_id.capitalize())
        form.set(name="alignment_file", value="align.fasta")
        form.set(name="alignment_format", value="FASTA")

        # currently the submission does not work due to reCAPTCHA
        browser.submit_selected(btnName="submit")

        page_text = browser.page
        page_text_list = str(page_text.find_all("p"))

        # https://regex101.com/r/rwcIl8/1
        new_url = re.findall(r"(https:.*)\"", page_text_list)[0]
        print(new_url)

        browser.close()
        # remove file in main directory for cleanliness
        os.unlink(filename)
        os.unlink("temp_align.fasta")
        os.unlink("align.fasta")
        os.unlink("blast_res.xml")

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
