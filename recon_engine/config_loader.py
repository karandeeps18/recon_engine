import json 
import os 

def load_config(path="config.json"):
    if not os.path.exists(path):
        raise FileNotFoundError("Config File Not Found")
    
    with open(path, 'r') as f:
        config = json.load(f)
        
    # basic requirements in the config checks 
    # openfigi api key, output and input paths, recon_dimension, start_data and end_date     
    # fail    
    return config 


# test
if __name__ == "__main__":
    test_config = load_config("config.json")