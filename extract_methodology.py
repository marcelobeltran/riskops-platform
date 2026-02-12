import pandas as pd
import os

file_path = r"c:\Users\Marcelo Beltran\Documents\IDEA\GIT\AuditorOperacional\riskops-platform-1\docs\Matriz escala de controles 2025 VB _admtarifa_ejemplo.xlsm"

def extract_logic(path):
    try:
        # 1. Inspect 'Escala controles'
        print("--- ESCALA CONTROLES ---")
        df_escala = pd.read_excel(path, sheet_name='Escala controles', engine='openpyxl')
        # Display the whole sheet as it's likely a small reference table
        print(df_escala.to_string())
        
        # 2. Inspect 'Umbrales' (if it exists as a separate sheet or within one)
        xl = pd.ExcelFile(path, engine='openpyxl')
        if 'Umbrales' in xl.sheet_names:
            print("\n--- UMBRALES ---")
            df_umbrales = pd.read_excel(path, sheet_name='Umbrales', engine='openpyxl')
            print(df_umbrales.to_string())
        else:
            print("\n'Umbrales' sheet not found, searching in others...")
            # Often it's in a hidden or specific sheet like 'Parametros'
            for s in xl.sheet_names:
                if any(k in s for k in ['Param', 'Config', 'Umbral']):
                    print(f"Checking potential sheet: {s}")
                    print(pd.read_excel(path, sheet_name=s, engine='openpyxl', nrows=10).to_string())

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_logic(file_path)
