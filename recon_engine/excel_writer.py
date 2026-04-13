"""excel_write.py creates multi-sheet excel report for two reconciliation dimensions (vehicle, strategy)
    sheets: Summary, Breaks, System A only, System_b only and Matched 
"""
import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


STYLING = {
    "header_font": Font(bold=True, color="FFFFFF"),
    "header_fill": PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid"),
    "title_font": Font(bold=True, size=14)
    }

