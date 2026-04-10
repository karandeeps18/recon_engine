# openfigi client api handeles the request  (from the system a using figi) and response from the api, normalize the calls
import requests

class OpenFigiClient:
    def __init__(self, api_key):
        self.url = "https://api.openfigi.com/v3/mapping"    
        self.header = {
            "Content-Type": "application/json",
            "X-OPENFIGI-APIKEY": api_key
        }
        
    def fetch(self, figis):
        # payload is figis in system A 
        for f in range(0, len(figis), 100):
            batch = figis[f:100]
            payload = [{"idType": "ID_BB_GLOBAL", "idValue": f} for f in batch]
        
        # response 
        response = requests.post(self.url, headers=self.header, json=payload)
        response.raise_for_status()
        return response.json()
