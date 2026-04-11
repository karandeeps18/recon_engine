# this is crossref table which saves the raw response into a reference table
# TODO: Create a robust filter logic currently using data_list[0]
# TODO: Add SCD2 or CrossRef Pattern - make Point-In-Time safe lookup - isActive, asOfDate  
import json 

def create_ticker_map(file_path):
    with open(file_path, 'r') as f:
        raw_data = json.load(f)
        
        ticker_map = {}
        for data in raw_data:
            data_list = data.get("data", [])
            if data_list:
                items = data_list[0]
                # later add filter logic to narrow down the response
                ticker_map[items['figi']] = items['ticker']
        return ticker_map
