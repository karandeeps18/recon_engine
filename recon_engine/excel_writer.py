import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

"""excel_write.py creates multi-sheet excel report for two reconciliation dimensions (vehicle, strategy)
    sheets: Summary, Breaks, System A only, System_b only and Matched 
"""
STYLE = {
    "header_font": Font(bold=True, color="FFFFFF"),
    "header_fill": PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid"),
    "title_font": Font(bold=True, size=14),
    "center_align": Alignment(horizontal="center")
}

def write_excel(recon_results, config):
    """ write excel file different sheets for summary and breaks"""
    output_path = config.get("output_file")
    wb = Workbook()
    
    # split sheets into 6 buckets for reporting 
    qty_breaks = recon_results[recon_results["status"] == "qty_break"]
    mv_breaks = recon_results[recon_results["status"] == "mv_break"]
    both_breaks = recon_results[recon_results["status"] == "both_breaks"]
    matched = recon_results[recon_results["status"] == "matched"]
    a_only = recon_results[recon_results["status"] == "system_a_only"]
    b_only = recon_results[recon_results["status"] == "system_b_only"]
    
    # summary sheet 
    ws = wb.active 
    ws.title = "Summary"
    
    total = len(recon_results)
    
    summary_rows = [
        ["Position Reconciliation Report"],
        [], 
        ["Recon Dimension", config.get("recon_dimension")], 
        ["Start Date", config.get("start_date")],
        ["End Date", config.get("end_date")],
        [],
        ["Status", "Count"],
        ["Match", len(matched)],
        ["Qty Break", len(qty_breaks)],
        ["MV Break", len(mv_breaks)],
        ["Both Break", len(both_breaks)],
        ["Missing in System B", len(a_only)],
        ["Missing in System A", len(b_only)],
        [],
        ["Total", total],
    ]
    
    # Dropping extra columns for each sheet
    qty_breaks = qty_breaks.drop(
        columns=["_merge", "status", "mv_diff"],
        errors="ignore"
    )
    mv_breaks = mv_breaks.drop(columns=["_merge", "status", "qty_diff"],
        errors="ignore"
    )
    both_breaks = both_breaks.drop(columns=["_merge", "status"],
        errors="ignore"
    )
    matched = matched.drop(columns=["_merge", "status"],
        errors="ignore"
    )
    a_only = a_only.drop(columns=["_merge", "status"],
        errors="ignore"
    )
    b_only = b_only.drop(columns=["_merge", "status"],
        errors="ignore"
    )
    
    for row in summary_rows:
        ws.append(row)

    # Detailed sheets 
    write_sheet(wb, "Quantity Breaks", qty_breaks)
    write_sheet(wb, "MV Breaks", mv_breaks)
    write_sheet(wb, "Both Breaks", both_breaks)
    write_sheet(wb, "Matched", matched)
    write_sheet(wb, "Missing in System B", a_only)
    write_sheet(wb, "Missing in System A", b_only)

    wb.save(output_path)
    
# write one df to one sheet in the workbook    
def write_sheet(wb, sheet_name, df):
    ws = wb.create_sheet(sheet_name)

    if df.empty:
        ws.append(["No records"])
        return

    # Header
    ws.append(list(df.columns))

    # Rows
    for row in df.itertuples(index=False, name=None):
        ws.append(row)

    # Freeze header row 
    ws.freeze_panes = "A2"