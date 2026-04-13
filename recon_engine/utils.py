# utils.py holds reusable utility functions 
import pandas as pd 

col_names = {"Strategy":  "strategy",
             "Vehicle" :  "vehicle",
             "Date"    :   "date",
             "FIGI"    : "figi",
             "Symbol"  : "symbol",
             "Quantity" : "quantity", 
             "Market Value" : "market_value"   
}

def normalize_df(df):
    """
    Normalize the data loading, enforce column names, convert date into datetime,
    strip white spaces and type cast for columns
    """
    df = df.rename(columns=col_names)
    df["date"] = pd.to_datetime(df["date"])
    df["quantity"] = df["quantity"].astype(float)
    df["market_value"] = df["market_value"].astype(float)

    # strip whitespace from all string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
        
    return df
