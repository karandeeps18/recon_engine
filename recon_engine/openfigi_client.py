"""openfigi client api handeles the request (from the system A using figi) and response from the api 
    1. session recieve requests 
    2. uses HTTPAdapter 
    3. adapter checks the retry logic 
    4. make requests 
    IF FAIL:
        - Check status code
        - if in force list -> retry 
        - wait with exp back-off 
    IF SUCCESS:
        - return response 
"""
import requests
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class OpenFigiClient:
    """
    Client for resolving FIGIs via OpenFigi 

    Features:
        - batch processing (max 100 per request)
        - Persistent HTTP session for connection reuse 
        - Automatic retry with exp back-off 
        - Retry Handles transient, network and overload errors explicitly defined
    """

    def __init__(self, api_key, batch_size=100):
        self.url = "https://api.openfigi.com/v3/mapping"
        self.batch_size = min(batch_size, 100)
        self.headers = {
            "Content-Type": "application/json",
            "X-OPENFIGI-APIKEY": api_key
        }

        # retry configuration
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            # list to include if the new override errors encoutered
            status_forcelist=[429, 500, 502, 503, 504],
            # since Openfigi uses POST method we need to explicit method for retry 
            allowed_methods=["POST"],
        )
    
        # for all the requests use the adapter with retry
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def fetch(self, figis):
        """resolve figi in batches, returns one response per figi request"""
        all_results = []

        # total_batches for logging
        total_batches = (len(figis) + self.batch_size - 1) // self.batch_size

        # payload is figis in system A
        for i in range(0, len(figis), self.batch_size):
            batch = figis[i: i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            payload = [{"idType": "ID_BB_GLOBAL", "idValue": figi} for figi in batch]

            logger.info("Batch %d / %d: %d", batch_num, total_batches, len(batch))

            try: 
                # response
                response = self.session.post(
                    self.url, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=30)
                response.raise_for_status()
                all_results.extend(response.json())
            
            # catch request level failure and continue, add the error to contract for downstream check 
            # network/api call errors
            except RequestException as e:
                logger.error("batch %d failed: %s", batch_num, e)
                all_results.extend([{"figi": figi, "error": str(e)} for figi in batch]) 
            
            # ValueError for response parsing     
            except ValueError as e:
                logger.error("batch %d failed parsing JSON: %s", batch_num, e)
                all_results.extend([{"figi": figi, "error": str(e)} for figi in batch]) 
            
            # small sleep time between batches     
            if batch_num < total_batches:
                time.sleep(0.24)
                
        logger.info("Fetch complete: %d responses for %d FIGIs", len(all_results), len(figis))
        return all_results