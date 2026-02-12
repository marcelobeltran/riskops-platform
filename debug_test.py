import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from risk_universe.models import Risk, Process, RiskCategory
from methodology.models import ProbabilityScale, ImpactScale, RiskLevel
from core.models import TimeStampedModel

def run_verification():
    print("--- Starting Verification ---")
    
    # 1. Inspect Risk Model fields runtime
    fields = [f.name for f in Risk._meta.fields]
    if 'code' not in fields:
        print("CRITICAL: 'code' field missing in Risk!")
        return
    if 'inherent_probability' not in fields:
        print("CRITICAL: 'inherent_probability' field missing!")
        return
    print("Risk Model Fields Verified.")

    # 2. CRUD Test
    # Get or create dependencies
    process, _ = Process.objects.get_or_create(name="Proceso Critico Test")
    category, _ = RiskCategory.objects.get_or_create(name="Fraude Externo")
    
    # Get Scales (Loaded via load_methodology_data)
    try:
        prob_3 = ProbabilityScale.objects.get(level=3) # Ocasional
    except ProbabilityScale.DoesNotExist:
        print("ERROR: Probability Scales not loaded! Run load_methodology_data.")
        return

    # Create Risk
    risk_code = "R-VERIFY-001"
    Risk.objects.filter(code=risk_code).delete()

    print(f"Creating Risk {risk_code}...")
    try:
        risk = Risk.objects.create(
            process=process,
            category=category,
            code=risk_code,
            title="Riesgo de Prueba Iteración 1",
            description="Verificando integración de metodología.",
            inherent_probability=prob_3,
            inherent_impact_level=4 # Medio Alto
        )
        print(f"Risk Created: {risk}")
        
        # Check Properties
        lvl_obj = risk.inherent_risk_level_obj
        if lvl_obj:
            print(f"Risk Level Calculated: {lvl_obj.name} (Color: {lvl_obj.color})")
        else:
             print("WARNING: No Risk Level calculated (Matrix mismatch?)")

    except Exception as e:
        print(f"FAILED to check Risk: {e}")
        return

    print("--- Verification Complete (SUCCESS) ---")

if __name__ == "__main__":
    run_verification()
