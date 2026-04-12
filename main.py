import sys 
import json
import logging
from recon_engine.config_loader import load_config
from recon_engine.reader import read_system_a, read_system_b
from recon_engine.openfigi_client import OpenFigiClient 
from recon_engine.cache import create_ticker_map
from recon_engine.cache import load_cache
from recon_engine.cache import save_cache
from recon_engine.recon import reconcile


logging.basicConfig(level=logging.INFO)


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
    valid_figi_a = sys_a[sys_a['isValidFigi']]
    invalid_figi_a = sys_a[~sys_a['isValidFigi']]
    logging.info("Total Invalid FIGI in System A: %s", len(invalid_figi_a))
    print(len(invalid_figi_a))
    # load cache 
    cache = load_cache(config['cache_file'])
    
    # check the valid unique figis in cache 
    unq_figis = valid_figi_a['figi'].unique().tolist()
    missing_figis = [f for f in unq_figis if f not in cache]
    
    # make calls for missing figis 
    if missing_figis:
        # call the openfigiclient 
        client = OpenFigiClient(api_key=config['openfigi_api_key'])
        
        # create raw_response object 
        raw_response = client.fetch(missing_figis)
        
        # store the raw response for check 
        inspect_file = config['inspect_file']
        with open(inspect_file, 'w') as f:
            json.dump(raw_response, f, indent=4)
            
        # call the cache to create a mapping table
        cache = create_ticker_map(inspect_file, existing_cache=cache)
        save_cache(cache, config['cache_file'])
    else:
        logging.info("FIGI present in Cache, No API Calls Needed")
        
    # reconcilation 
    reconciled = reconcile(sys_a, sys_b, cache, config)
    reconciled.to_csv("/Users/karandeepsonewane/Projects/Recon_engine/output/reconciled_veh.csv")

if __name__ == "__main__":
    main()