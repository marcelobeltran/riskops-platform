import pandas as pd
import os

file_path = r"c:\Users\Marcelo Beltran\Documents\IDEA\GIT\AuditorOperacional\riskops-platform-1\docs\Matriz escala de controles 2025 VB _admtarifa_ejemplo.xlsm"

def dump_logic(path):
    try:
        xl = pd.ExcelFile(path, engine='openpyxl')
        
        print("=== HOJA: Escala controles ===")
        df_e = pd.read_excel(path, sheet_name='Escala controles', engine='openpyxl')
        print(df_e.to_string())
        
        print("\n=== HOJA: Matriz ROP (HEADERS) ===")
        # Usually headers start around row 5-10
        df_m = pd.read_excel(path, sheet_name='Matriz ROP', engine='openpyxl', header=None, nrows=15)
        for i, row in df_m.iterrows():
            print(f"Row {i}: {[str(x) for x in row.values if pd.notnull(x)]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_logic(file_path)
