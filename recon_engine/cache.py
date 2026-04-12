import json
import os 

def create_ticker_map(file_path, existing_cache=None):
    with open(file_path, 'r') as f:
        raw_data = json.load(f)
        cache = existing_cache or {}
        
        # loop over list of dict response from openfigi raw response
        for data in raw_data:
            # skip figis with error in api response  
            if data.get("error"):
                continue
            
            # api response under data       
            data_list = data.get("data", [])
            if not data_list:
                continue 
            
            # case 1: single match  
            if len(data_list) == 1:
                record = data_list[0]
                
            # case 2: multiple match 
            else: 
                record = None 
                for d in data_list:
                    if d.get("exchCode") == "US" and d.get("securityType") == "Common Stock":
                        record = d
                        break 
                    
                    # fall back if its not matched 
                    if record is None:
                        record = data_list[0]
                        
            figi = record.get("figi")
            ticker = record.get("ticker")
    
            # if figi:ticker exists save  
            if figi and ticker:
                cache[figi] = ticker
        return cache


def load_cache(path):
    """
    load existing cache from the disk, if not found return empty {} 
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            cache = json.load(f)
            return cache 
    except FileNotFoundError:
        return {}

def save_cache(data, path):
    """
    persistent cache stored in the disk with figi:ticker mapping 
    """
    # directory exists 
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, sort_keys=True)