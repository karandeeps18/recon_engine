# reader.py reads the data from both System_A and System_B
import pandas as pd
import json
import logging
from recon_engine.utils import normalize_df

logger = logging.getLogger(__name__)

# read system A and normalize
def read_system_a(filepath):
    sys_a = pd.read_csv(filepath)
    sys_a = normalize_df(sys_a)

    # handling bad data at source: figis are null or empty
    bad_figis = sys_a["figi"].isna() | (sys_a["figi"] == "")
    if bad_figis.any():
        logger.warning(f"Total Empty/Null FIGIs in Sys A: {bad_figis.sum()}")
    sys_a['isValidFigi'] = ~bad_figis

    logger.info(f"System A: {len(sys_a)} rows, {sys_a['figi'].nunique()} FIGIs")
    return sys_a

# read system b and normalize
def read_system_b(filepath):
    with open(filepath, 'r') as f:
        raw_data = json.load(f)
    
    if not isinstance(raw_data, dict) or "data" not in raw_data:
        raise ValueError("System B JSON must contain top-level 'data' array")
        
    sys_b = pd.DataFrame(raw_data['data'])
    sys_b = normalize_df(sys_b)

    logger.info(f"System A: {len(sys_b)} rows, {sys_b['symbol'].nunique()} Symbols")
    return sys_b
