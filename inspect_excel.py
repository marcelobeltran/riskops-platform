import pandas as pd
import os

file_path = r"c:\Users\Marcelo Beltran\Documents\IDEA\GIT\AuditorOperacional\riskops-platform-1\docs\Matriz escala de controles 2025 VB _admtarifa_ejemplo.xlsm"

def inspect_excel(path):
    if not os.path.exists(path):
        print(f"Error: File not found at {path}")
        return

    try:
        # Load the workbook to get sheet names
        xl = pd.ExcelFile(path, engine='openpyxl')
        print(f"File found: {os.path.basename(path)}")
        print(f"Sheets: {xl.sheet_names}")
        print("-" * 30)

        for sheet in xl.sheet_names:
            print(f"\nInspecting Sheet: {sheet}")
            # Read first few rows to see headers and data
            df = pd.read_excel(path, sheet_name=sheet, engine='openpyxl', nrows=5)
            print("Columns found:")
            print(df.columns.tolist())
            print("\nSample Data (First 2 rows):")
            print(df.head(2).to_string())
            print("-" * 30)

    except Exception as e:
        print(f"Error reading Excel: {e}")

if __name__ == "__main__":
    inspect_excel(file_path)
