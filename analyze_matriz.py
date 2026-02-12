import pandas as pd
import os

file_path = r"c:\Users\Marcelo Beltran\Documents\IDEA\GIT\AuditorOperacional\riskops-platform-1\docs\Matriz escala de controles 2025 VB _admtarifa_ejemplo.xlsm"

def find_matriz_rop(path):
    try:
        xl = pd.ExcelFile(path, engine='openpyxl')
        target = [s for s in xl.sheet_names if 'Matriz ROP' in s]
        if target:
            sheet = target[0]
            print(f"Reading Sheet: {sheet}")
            # The matrix often starts after some header rows
            df = pd.read_excel(path, sheet_name=sheet, engine='openpyxl', header=None, nrows=20)
            for i, row in df.iterrows():
                row_vals = [str(x) for x in row.values if pd.notnull(x)]
                if 'N°' in row_vals or 'Proceso' in row_vals or 'RIESGO' in row_vals:
                    print(f"Header possibly at row {i}")
                    df_actual = pd.read_excel(path, sheet_name=sheet, engine='openpyxl', skiprows=i)
                    print("COLUMNS:")
                    print(df_actual.columns.tolist())
                    print("\nDATA SAMPLE (Row 0):")
                    print(df_actual.iloc[0].to_string())
                    break
        else:
            print(f"Sheet 'Matriz ROP' not found. Available: {xl.sheet_names}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_matriz_rop(file_path)
