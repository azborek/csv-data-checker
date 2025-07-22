import base64
import pandas as pd
import io
import openpyxl
import datetime
from openpyxl.styles import PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo

def handler(request):
    try:
        body = request.json()
        csv_base64 = body["csv_content"]

        # Decode base64 CSV
        csv_bytes = base64.b64decode(csv_base64)
        df = pd.read_csv(io.BytesIO(csv_bytes), parse_dates=["lastused"])

        # Filter: lastused must be within past 60 days
        cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=60)
        df = df[df["lastused"].notna() & (df["lastused"].dt.tz_localize(None) >= cutoff)]

        # Define field pairs to compare
        like_pairs = [
            ("email", "email-forced"),
            ("phone", "phone-forced"),
            ("title", "title-forced"),
            ("name", "name-forced"),
            ("mobile", "mobile-forced"),
        ]

        # Keep only relevant columns
        keep_cols = {"username"}
        for orig, forced in like_pairs:
            keep_cols.update([orig, forced])
        df = df[[col for col in df.columns if col in keep_cols]]

        # Sort by username
        df = df.sort_values("username")

        # Create Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Differences"

        # Write data to sheet
        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        # Insert table
        ref = f"A1:{openpyxl.utils.get_column_letter(ws.max_column)}{ws.max_row}"
        tab = Table(displayName="DiffTable", ref=ref)
        tab.tableStyleInfo = TableStyleInfo(
            name="TableStyleMedium9", showFirstColumn=False, showLastColumn=False,
            showRowStripes=True, showColumnStripes=False
        )
        ws.add_table(tab)

        # Autofit columns
        for col in ws.columns:
            max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_len + 2

        # Highlight mismatched forced fields
        yellow = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        for i, row in enumerate(df.itertuples(index=False), start=2):
            for orig, forced in like_pairs:
                if getattr(row, orig, "") != getattr(row, forced, ""):
                    col_letter = openpyxl.utils.get_column_letter(df.columns.get_loc(forced) + 1)
                    ws[f"{col_letter}{i}"].fill = yellow

        # Save Excel to bytes
        excel_bytes = io.BytesIO()
        wb.save(excel_bytes)
        excel_bytes.seek(0)

        # Save CSV to bytes
        output_csv_bytes = df.to_csv(index=False).encode()

        # Generate timestamped filenames
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        csv_name = f"output2_{timestamp}.csv"
        excel_name = f"output2_{timestamp}.xlsx"

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {
                "output_csv_name": csv_name,
                "output_excel_name": excel_name,
                "csv_base64": base64.b64encode(output_csv_bytes).decode(),
                "excel_base64": base64.b64encode(excel_bytes.read()).decode()
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }
