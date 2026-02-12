import pandas as pd
import os

file_path = r"c:\Users\Marcelo Beltran\Documents\IDEA\GIT\AuditorOperacional\riskops-platform-1\docs\Matriz escala de controles 2025 VB _admtarifa_ejemplo.xlsm"

def extract_exact_params(path):
    try:
        # Load the Escala controles sheet
        df = pd.read_excel(path, sheet_name='Escala controles', engine='openpyxl')
        print("--- ESCALA CONTROLES FULL ---")
        print(df.head(20).to_string())
        
        # Try to find the weights row or table
        # Searching for 'Ponderación' or similar
        weights = {}
        target_cols = ['Oportunidad', 'Alcance', 'Tipo de control', 'Segregación de funciones', 'Formalización']
        
        # Find where headers are
        for i, row in df.iterrows():
            row_vals = [str(x) for x in row.values]
            if any('Oportunidad' in str(x) for x in row_vals):
                print(f"\nFound Weights Header at row {i}")
                # Often weights are in the row above or below
                print(df.iloc[i-1:i+2].to_string())
                break
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_exact_params(file_path)
