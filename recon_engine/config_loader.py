# config_loader.py loads the config.json for requirements 
import json 
import os 

def load_config(path="config.json"):
    if not os.path.exists(path):
        raise FileNotFoundError("Config File Not Found")
    
    with open(path, 'r') as f:
        config = json.load(f)   
        
    # validate required keys
    required = ["openfigi_api_key", "system_a_file", "system_b_file",
                "recon_dimension", "start_date", "end_date", "output_file"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError(f"Missing config keys: {missing}")
    return config 