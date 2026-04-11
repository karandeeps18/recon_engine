import sys 
import json
from recon_engine.config_loader import load_config
from recon_engine.reader import read_system_a, read_system_b
from recon_engine.openfigi_client import OpenFigiClient 
from recon_engine.crossref import create_ticker_map


def main():
    """_summary_
    This is the main entry point for the reconciliation engine 
    This will orchestrate the loading, fetching, caching, reconciliation, and Output 
    """
    # Load config.json 
    config = load_config("config.json")
    # load system a and system b 
    # later need to add the file handling using glob 
    print(config)
    sys_a = read_system_a(config['system_a_file'])
    sys_b = read_system_b(config['system_b_file'])
    print(sys_a.head())
    print(sys_b.head())
    
    # extract unique figis from the system A 
    unq_figis = sys_a['figi'].unique().tolist()
    
    # top 10 figis only --------------------- change later -------------
    # unq_figis = unq_figis[:10]
    
    # call the openfigiclient 
    client = OpenFigiClient(api_key=config['openfigi_api_key'])
    
    # create raw_response object 
    raw_response = client.fetch(unq_figis)
    
    # store the raw response for check 
    inspect_file = config['inspect_file']
    with open(inspect_file, 'w') as f:
            json.dump(raw_response, f, indent=4)
            
    # call the cross ref to create a mapping table
    refTable = create_ticker_map(inspect_file)
    
    
    with open(config['cache_file'], 'w') as f:
        json.dump(refTable, f, indent=4)
    
    return sys_a, sys_b, config

if __name__ == "__main__":
    main()