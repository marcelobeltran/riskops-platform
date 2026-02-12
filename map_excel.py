import pandas as pd
import os

file_path = r"c:\Users\Marcelo Beltran\Documents\IDEA\GIT\AuditorOperacional\riskops-platform-1\docs\Matriz escala de controles 2025 VB _admtarifa_ejemplo.xlsm"

def find_headers_and_sample(path):
    try:
        xl = pd.ExcelFile(path, engine='openpyxl')
        print(f"Sheet Names: {xl.sheet_names}")
        
        # Focus on the first few sheets as they are usually the main ones
        for sheet in xl.sheet_names[:3]:
            print(f"\n--- ANALYZING SHEET: {sheet} ---")
            df = pd.read_excel(path, sheet_name=sheet, engine='openpyxl', nrows=20, header=None)
            
            # Find a row that looks like a header (contains 'Riesgo' or 'Control' or 'Proceso')
            header_row_index = 0
            for i, row in df.iterrows():
                row_str = " ".join([str(x) for x in row.values if pd.notnull(x)])
                if any(k in row_str for k in ['Riesgo', 'Control', 'Proceso', 'PROCESO', 'RIESGO']):
                    header_row_index = i
                    print(f"Potential Header found at row {i}: {row_str[:200]}...")
                    break
            
            # Reload with correct header
            df_actual = pd.read_excel(path, sheet_name=sheet, engine='openpyxl', skiprows=header_row_index)
            print(f"Actual Columns: {df_actual.columns.tolist()[:15]}... (showing first 15)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_headers_and_sample(file_path)
