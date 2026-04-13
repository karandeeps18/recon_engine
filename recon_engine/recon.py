import pandas as pd

# """ Summary of Reconcilitation Workflow
#     1. filter the sys_a data based on isValid flag for the 
#     2. filter by date using config start and end dates 
#     3. if recon by vehicle -> aggregate + join key = [strategy, vehicle, symbol, date] 
#         if recon by strategy -> aggregate by strategy + join key = [strategy, symbol, date]
#     4. clasify based on outer join
#         if matched then 'match'
#         if break - qty break, mv_break, both_break, matched
#         if orphan - exists in system_a_only or system_b_only
#     """

def reconcile(sys_a, sys_b, cache, config):
    """
    Reconcile positions between System A and System B
    Supports vehicle and strategy-level dimensions
    Returns DataFrame with qty_break, mv_break, and status columns
    """
    
    # filter data for only valid Figi 
    sys_a = sys_a[sys_a['isValidFigi']].copy()
    
    # enrich sys_a with symbols from cahche 
    sys_a['symbol'] = sys_a['figi'].map(cache)
    sys_a = sys_a[sys_a['symbol'].notna()].copy()
    
    # filter both the system for config start and end date 
    start_date = pd.to_datetime(config['start_date']) 
    end_date = pd.to_datetime(config['end_date'])
    
    sys_a = sys_a[(sys_a['date'] >= start_date) & (sys_a['date'] <= end_date)].copy()   
    sys_b = sys_b[(sys_b['date'] >= start_date) & (sys_b['date'] <= end_date)].copy()   
    
    # if recon_dimension is vehicle merge on all keys, else merge aggregated view on strategy, date, symbol
    if config['recon_dimension'] == 'vehicle':
        
        # aggreagted on vehicle level to avoid row exlposion 
        sys_a_agg = sys_a.groupby(['strategy', 'vehicle', 'date', 'symbol'],
                                  as_index=False).agg(
                                  quantity_a=('quantity', 'sum'),
                                  market_value_a=('market_value', 'sum')
                                )
        
        sys_b_agg = sys_b.groupby(['strategy', 'vehicle', 'date', 'symbol'],
                                  as_index=False).agg(
                                  quantity_b=('quantity', 'sum'),
                                  market_value_b=('market_value', 'sum')
                                )

        merged = pd.merge(sys_a_agg, 
                            sys_b_agg, 
                            on=['strategy', 'vehicle', 'symbol', 'date'],
                            how="outer", 
                            suffixes=("_a", "_b"), 
                            indicator=True)
        
    else:
        # aggregat sys_a and sys_b on ['strategy', 'date', 'symbol'] to get strategy view
        sys_a_agg = sys_a.groupby(['strategy', 'date', 'symbol'],
                                    as_index=False).agg(
                                    quantity_a= ('quantity', 'sum'), 
                                    market_value_a = ('market_value', 'sum')
                                  )
                                  
        sys_b_agg = sys_b.groupby(['strategy', 'date', 'symbol'],
                                    as_index=False).agg(
                                    quantity_b= ('quantity', 'sum'), 
                                    market_value_b = ('market_value', 'sum')
                                  )
        
        # merge aggreagted for recon by strategy
        merged = pd.merge(sys_a_agg, 
                            sys_b_agg, 
                            on=['strategy', 'date', 'symbol'],
                            how="outer", 
                            indicator=True)
    # converting categorical _merge into str for manipulation
    merged['_merge'] = merged['_merge'].astype(str)
    
    # for row level match - to find out orphan in System A or System B 
    # status map for lookup 
    status_map = {
        "both":       "matched",
        "left_only":  "system_a_only",
        "right_only": "system_b_only" }
    
    # mapping based on flag 
    merged['status'] = merged['_merge'].map(status_map)
    
    # reconciliation based on the merged data abive 
    merged['qty_break'] = merged['quantity_a'].fillna(0) - merged['quantity_b'].fillna(0)
    merged['mv_break'] = merged['market_value_a'].fillna(0) - merged['market_value_b'].fillna(0)
    
    # Reconciliation breaks - classification 
    #   1. qty_break != 0 and mv_break == 0 (+ tolerance) - as qty_break 
    #   2. mv_break != 0 (+ tolerance) and qty_break = 0 - as mv_break 
    #   3. qty_break != 0 and mv_break != 0 (+ tolerance) - as both_break 
    # get the config tolerance for mv_break 
    mv_tolerance = config.get('tolerance_market_value', 0)
    
    # base case: records present in both the systems 
    both_mask = merged["_merge"] == "both"
    
    # masks for qty difference and mv difference with tolerance 
    mask_qty_diff = merged["qty_break"] != 0
    mv_differs = merged["mv_break"].abs() > mv_tolerance
    
    # Apply the classification for the break 
    # 1. qty break only 
    mask_qty_diff_only = both_mask & mask_qty_diff & ~mv_differs
    merged.loc[mask_qty_diff_only, "status"] = 'qty_break' 
    
    # 2. mv break only 
    mask_mv_break_only = both_mask & mv_differs & ~mask_qty_diff
    merged.loc[mask_mv_break_only, "status"] = 'mv_break'
    
    # 3. both break 
    mask_both_break = both_mask & mask_qty_diff & mv_differs
    merged.loc[mask_both_break, "status"] = 'both_breaks'
    
    # 4. perfect match 
    mask_perfect_match = both_mask & ~mask_qty_diff & ~mv_differs
    merged.loc[mask_perfect_match, "status"] = 'matched'
        
    return merged