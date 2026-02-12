import pandas as pd
import os

file_path = r"c:\Users\Marcelo Beltran\Documents\IDEA\GIT\AuditorOperacional\riskops-platform-1\docs\Matriz escala de controles 2025 VB _admtarifa_ejemplo.xlsm"

def get_scales_clean(path):
    try:
        df = pd.read_excel(path, sheet_name='Escala controles', engine='openpyxl')
        # Remove empty rows and empty columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Search for keywords
        for keyword in ['Oportunidad', 'Alcance', 'Tipo de control', 'Segregación']:
            matches = df[df.apply(lambda row: row.astype(str).str.contains(keyword).any(), axis=1)]
            if not matches.empty:
                print(f"\n--- MATCH FOR {keyword} ---")
                print(matches.to_string())
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_scales_clean(file_path)
