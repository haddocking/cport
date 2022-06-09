"""CSM_POTENTIAL module for API interaction."""
import json
import logging
import sys
import time

import pandas as pd
import requests

from cport.url import CSM_POTENTIAL_URL

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 30  # seconds
NUM_RETRIES = 12
ELEMENT_LOAD_WAIT = 5  # seconds


class CsmPotential:
    """CSM_POTENTIAL class."""

    def __init__(self, pdb_file, chain_id):
        """
        Initialize the class.

        Parameters
        ----------
        pdb_file : str
            Path to PDB file.
        chain_id : str
            Chain identifier.
        pdb_file : str
            Path to pdb file.

        """
        self.chain_id = chain_id
        self.pdb_file = pdb_file
        self.wait = WAIT_INTERVAL
        self.tries = NUM_RETRIES

    def submit(self):
        """
        Submit request for results.

        Returns
        -------
        results.text : string
            A string containing protein interaction
            prediction results.

        """
        data = {"pdb_file": open(self.pdb_file)}

        req = requests.post(CSM_POTENTIAL_URL, files=data)

        response = req.json()
        if response["job_id"]:
            # successful submission
            job_id = response["job_id"]
        else:
            # failed submission
            sys.exit()

        return job_id

    def retrieve_prediction(self, job_id=None):
        """
        Wait for the results to be available.

        Parameters
        ----------
        job_id : string
            The id assigned by the csm-potential server.

        Returns
        -------
        response : dict
            A dict containing the chains and the predictions.

        """
        data = {"job_id": job_id}
        completed = False
        while not completed:
            # Check if the result page exists
            req = requests.get(CSM_POTENTIAL_URL, data=data)
            response = req.json()
            if "status" not in response:
                completed = True

            if self.tries == 0:
                # if tries is 0, then the server is not responding
                log.error(
                    f"CSM-Potential server is not responding, job id was {job_id}"
                )
                sys.exit()

            else:
                # still running, wait a bit
                log.debug(f"Waiting for CSM-Potential to finish... {self.tries}")
                time.sleep(self.wait)
                self.tries -= 1

        return response

    def parse_prediction(self, prediction=None, test_file=None):
        """
        Take the result and parse them into the prediction dictionary.

        Parameters
        ----------
        prediction : dict
            Dict containing the interaction prediction for each chain.
        test_file : string
            The path to the test file.

        Returns
        -------
        prediction_dict : dict
            The dictionary containing the parsed prediction results with active
            and passive sites.

        """
        prediction_dict = {"active": [], "passive": []}
        key = "Chain " + self.chain_id

        if test_file:
            # for testing purposes
            with open(test_file) as f:
                data = f.read()
            results = json.loads(data)[key]
        else:
            results = prediction[key]

        result_dict = pd.DataFrame.from_dict(results)

        for row in result_dict.itertuples():
            # the webserver uses any value above 0.5 to indicate interaction
            if row.prediction >= 0.5:
                interaction = True
                # adds standardized score to positive residues
                score = row.prediction
            else:
                interaction = False

            residue_number = row.resnumber
            if interaction:
                prediction_dict["active"].append([int(residue_number), float(score)])
            elif not interaction:
                prediction_dict["passive"].append(int(residue_number))
            else:
                log.warning(
                    f"There appears that residue {row} is either empty or unprocessable"
                )

        return prediction_dict

    def run(self):
        """
        Execute the csm-potential prediction.

        Returns
        -------
        prediction_dict : dict
            A dictionary containing the raw prediction results.

        """
        log.info("Running CSM-Potential")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        job_id = self.submit()
        results = self.retrieve_prediction(job_id=job_id)
        prediction_dict = self.parse_prediction(prediction=results)

        return prediction_dict
