# reconciliation.py joins System A and System B using crossReference table for mapping 
# Reconile the positions based on "Strategy" and "Vehicle"
import pandas as pd
import json
from config_loader import load_config


col_names = {"Strategy":  "strategy",
             "Vehicle" :  "vehicle",
             "Date"    :   "date",
             "FIGI"    : "figi",
             "Symbol"  : "symbol",
             "Quantity" : "quantity", 
             "Market Value" : "market_value"   
}
# def recon_run(start_date, end_date, system_a, system_b, cross_ref, recon_dimension="strategy"):
    
sys_a = pd.read_csv('data/system_a/system_a_posns.csv')
sys_a = sys_a.rename(columns=col_names)
    # type enforcement 
sys_a["date"] = pd.to_datetime(sys_a["date"])
sys_a["quantity"] = sys_a["quantity"].astype(dtype=float)
sys_a["market_value"] = sys_a["market_value"].astype(dtype=float)
print("Total Unique FIGIs", sys_a["figi"].nunique())

with open('data/system_b/system_b_posns.json', 'r') as f:
    raw_data = json.load(f)
sys_b = pd.DataFrame(raw_data['data'])
sys_b = pd.DataFrame(raw_data['data'])
sys_b = sys_b.rename(columns=col_names)
sys_b["date"] = pd.to_datetime(sys_b["date"])
sys_b["quantity"] = sys_b["quantity"].astype(dtype=float)
sys_b["market_value"] = sys_b["market_value"].astype(dtype=float)


with open('data/mappings/figi_cache.json', 'r') as f:
    cross_ref = json.load(f)
cross_ref = pd.DataFrame(cross_ref.items(), columns=['figi','symbol'])


# merge 
merged_b = pd.merge(sys_b, 
                    cross_ref, 
                    on='symbol', 
                    how='left')
recon_table = pd.merge(sys_a, 
                       merged_b, 
                        on=["strategy", "vehicle", "date", "figi"],
                       how='outer',
                       suffixes=("_a", "_b"),
                       indicator=True
                       )

recon_table["qty_diff"] = recon_table["quantity_a"].fillna(0) - recon_table["quantity_b"].fillna(0)
recon_table["mv_diff"] = recon_table["market_value_a"].fillna(0) - recon_table["market_value_b"].fillna(0)



# print(sys_a) 
# print(sys_b)
# print(cross_ref)
print(recon_table.head(5))
