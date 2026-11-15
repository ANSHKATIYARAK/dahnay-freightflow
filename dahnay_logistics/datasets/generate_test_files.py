"""
Generates realistic multi-format test files for DahNAY Logistics:
- sample_dahnay_si.xlsx (Excel with merged cells & formulas)
- sample_dahnay_si.txt (Plaintext / email format)
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

os.makedirs("dahnay_logistics/datasets", exist_ok=True)

# 1. Generate Excel SI
wb = Workbook()
ws = wb.active
ws.title = "Shipping_Instruction"

# Styling
title_font = Font(name="Arial", size=14, bold=True, color="1E3A8A")
header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
bold_font = Font(name="Arial", size=10, bold=True)
regular_font = Font(name="Arial", size=10)

ws["A1"] = "DAHNAY LOGISTICS - EXPORT SHIPPING INSTRUCTIONS"
ws["A1"].font = title_font

ws["A3"] = "Booking Ref:"
ws["B3"] = "BKG-MAA-992104"
ws["B3"].font = bold_font

ws["A4"] = "Shipper:"
ws["B4"] = "Tirupur Garments Export Ltd, SIDCO Industrial Estate, Tirupur, Tamil Nadu"

ws["A5"] = "Consignee:"
ws["B5"] = "Gulf Retail Fashion LLC, Jebel Ali Free Zone, Dubai, UAE"

ws["A6"] = "Port of Loading:"
ws["B6"] = "Chennai Port (INMAA)"

ws["A7"] = "Port of Discharge:"
ws["B7"] = "Jebel Ali Port (AEJEA)"

ws["A8"] = "Vessel / Voyage:"
ws["B8"] = "MSC EMANUELA / 2408W"

ws["A9"] = "Cargo Description:"
ws["B9"] = "100% Cotton Knitted Finished T-Shirts (HS Code: 6109.10)"

ws["A10"] = "Gross Weight:"
ws["B10"] = 26800.0  # kg

ws["A11"] = "Volume (CBM):"
ws["B11"] = 64.2

# Container Table Headers
headers = ["Container No.", "Seal No.", "Type", "Packages", "Gross Weight (KGS)", "CBM"]
for col_idx, h in enumerate(headers, start=1):
    cell = ws.cell(row=13, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center")

# Rows
row1 = ["MSCU9081245", "SL982103", "40HC", 460, 13400.0, 32.1]
row2 = ["MEDU4091823", "SL982104", "40HC", 460, 13400.0, 32.1]

for col_idx, val in enumerate(row1, start=1):
    ws.cell(row=14, column=col_idx, value=val)

for col_idx, val in enumerate(row2, start=1):
    ws.cell(row=15, column=col_idx, value=val)

excel_path = "dahnay_logistics/datasets/sample_dahnay_si.xlsx"
wb.save(excel_path)
print(f"✔ Generated realistic Excel SI: {excel_path}")

# 2. Text SI
text_content = """DAHNAY LOGISTICS EXPORT SHIPPING INSTRUCTIONS
Booking Reference: BKG-MAA-992104
Shipper Name: Tirupur Garments Export Ltd
Shipper Address: Plot 14, SIDCO Industrial Estate, Tirupur, Tamil Nadu 641603
Consignee Name: Gulf Retail Fashion LLC
Consignee Address: P.O. Box 9821, Jebel Ali Free Zone, Dubai, UAE
Port of Loading: Chennai Port (INMAA)
Port of Discharge: Jebel Ali Port (AEJEA)
Vessel: MSC EMANUELA
Voyage: 2408W
Total Packages: 920 Cartons
Gross Weight: 26800 KGS
Measurement: 64.2 CBM
Goods Description: 100% Cotton Knitted Finished T-Shirts
HS Code: 6109.10
Freight Terms: PREPAID

CONTAINER DETAILS:
1. MSCU9081245 / SL982103 / 40HC / 460 PKGS / 13400 KGS / 32.1 CBM
2. MEDU4091823 / SL982104 / 40HC / 460 PKGS / 13400 KGS / 32.1 CBM
"""

txt_path = "dahnay_logistics/datasets/sample_dahnay_si.txt"
with open(txt_path, "w", encoding="utf-8") as f:
    f.write(text_content)
print(f"✔ Generated text SI: {txt_path}")
