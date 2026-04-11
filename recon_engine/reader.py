# reader.py reads the data from both System_A and System_B
import pandas as pd  
import json 

col_names = {"Strategy":  "strategy",
             "Vehicle" :  "vehicle",
             "Date"    :   "date",
             "FIGI"    : "figi",
             "Symbol"  : "symbol",
             "Quantity" : "quantity", 
             "Market Value" : "market_value"   
}

# read system a 
def read_system_a(filepath):
    sys_a = pd.read_csv(filepath)
    # TODO: normalize the column names for handling 
    # strategy, vehicle, date, figi, quantity, market_value  
    sys_a = sys_a.rename(columns=col_names)
    # type enforcement 
    sys_a["date"] = pd.to_datetime(sys_a["date"])
    sys_a["quantity"] = sys_a["quantity"].astype(dtype=float)
    sys_a["market_value"] = sys_a["market_value"].astype(dtype=float)
    print("Total Unique FIGIs", sys_a["figi"].nunique())
    return sys_a


# read system b 
def read_system_b(filepath):
    with open(filepath, 'r') as f:
        raw_data = json.load(f)
    sys_b = pd.DataFrame(raw_data['data'])
    sys_b = sys_b.rename(columns=col_names)
    sys_b["date"] = pd.to_datetime(sys_b["date"])
    sys_b["quantity"] = sys_b["quantity"].astype(dtype=float)
    sys_b["market_value"] = sys_b["market_value"].astype(dtype=float)
    print("System B total Unique Tickers:", sys_b['symbol'].nunique())
    # print("sys_b:", sys_b)
    return sys_b


# test 
if __name__ == "__main__":
    sysb = read_system_b("data/system_b/system_b_posns.json")
    sysa = read_system_a("data/system_a/system_a_posns.csv")
    print("sysb:", sysb.head(5))
    print("sysa:", sysa.head(5))
