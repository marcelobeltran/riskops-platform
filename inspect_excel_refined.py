import pandas as pd
import os

file_path = r"c:\Users\Marcelo Beltran\Documents\IDEA\GIT\AuditorOperacional\riskops-platform-1\docs\Matriz escala de controles 2025 VB _admtarifa_ejemplo.xlsm"

def inspect_excel_refined(path):
    try:
        xl = pd.ExcelFile(path, engine='openpyxl')
        for sheet in xl.sheet_names:
            print(f"SHEET: {sheet}")
            df = pd.read_excel(path, sheet_name=sheet, engine='openpyxl', nrows=1)
            print(f"COLUMNS: {df.columns.tolist()}")
            print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_excel_refined(file_path)
