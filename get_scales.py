import pandas as pd
import os

file_path = r"c:\Users\Marcelo Beltran\Documents\IDEA\GIT\AuditorOperacional\riskops-platform-1\docs\Matriz escala de controles 2025 VB _admtarifa_ejemplo.xlsm"

def get_scales(path):
    try:
        # Load the sheet. Use header=None to see everything if it's messy.
        df = pd.read_excel(path, sheet_name='Escala controles', engine='openpyxl')
        print("--- ESCALA CONTROLES FULL DUMP ---")
        print(df.to_string())
        
        # Look for the specific naming: "Oportunidad", "Alcance", etc.
        # They are usually labels followed by values like 100%, 50%, 0%.
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_scales(file_path)
