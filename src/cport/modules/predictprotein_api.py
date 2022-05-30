import json
import logging
import requests

import pandas as pd

from cport.modules import utils
from cport.modules.utils import get_fasta_from_pdbid
from cport.url import PREDICTPROTEIN_API
from io import StringIO
from xml.etree.ElementTree import tostring

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 10  # seconds
NUM_RETRIES = 12
ELEMENT_LOAD_WAIT = 5  # seconds


class Predictprotein_api:
    """PREDICTPROTEIN class."""

    def __init__(self, pdb_id, chain_id):
        """
        Initialize the class.

        Parameters
        ----------
        pdb_id : str
            Protein data bank identification code.
        chain_id : str
            Chain identifier.

        """
        self.pdb_id = pdb_id
        self.chain_id = chain_id
        self.wait = WAIT_INTERVAL
        self.tries = NUM_RETRIES

    def submit(self):
        """
        Submits request for results.

        Returns
        -------
        results.text : string
            A string containing protein interaction
            prediction results.

        """
        sequence = get_fasta_from_pdbid(self.pdb_id, self.chain_id)
        # FASTA header must be removed from sequence
        sequence_headless = "".join(sequence.splitlines(keepends=True)[1:])

        log.info(sequence_headless)

        data = {"action": "get", "sequence": sequence_headless, "file": "query.prona"}

        results = requests.post(PREDICTPROTEIN_API, data=json.dumps(data))

        return results.text

    @staticmethod
    def parse_prediction(prediction=None, test_file=None):
        """
        Take the result and parses them into the prediction dictionary.

        Parameters
        ----------
        prediction : string
            String containing the interaction prediction.
        test_file : str
            The path to the test file.

        Returns
        -------
        prediction_dict : dict
            The dictionary containing the parsed prediction results with active
            and passive sites.

        """
        prediction_dict = {"active": [], "passive": []}

        if test_file:
            # for testing purposes
            result_file = test_file
        else:
            result_file = StringIO(prediction)

        final_predictions = pd.read_csv(
            result_file,
            skiprows=11,
            usecols=[0, 2, 3],
            names=["Residue_Number", "Protein_RI", "Protein_Pred"],
            delim_whitespace=True,
        )

        for row in final_predictions.itertuples():
            # 1 indicates interaction
            if row.Protein_Pred == 1:
                interaction = True
                # adds standardized score to positive residues
                score = row.Protein_RI / 100
            else:
                interaction = False

            residue_number = int(row.Residue_Number.split("_")[-1])
            if interaction:
                prediction_dict["active"].append([residue_number, score])
            elif not interaction:
                prediction_dict["passive"].append(residue_number)
            else:
                log.warning(
                    f"There appears that residue {row} is either empty or unprocessable"
                )

        return prediction_dict

    def run(self):
        """
        Execute the PredictProtein prediction.

        Returns
        -------
        prediction_dict : dict
            A dictionary containing the raw prediction results.

        """
        log.info("Running PredictProtein")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        prediction = self.submit()
        prediction_dict = self.parse_prediction(prediction=prediction)

        return prediction_dict
