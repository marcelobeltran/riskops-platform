import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from risk_universe.models import Process, RiskOwner, HistoricalProcess
from django.db import connection

def recover():
    print("Starting recovery from History...")
    processes = Process.objects.all()
    count = 0
    
    # Cache existing owners
    owners_map = {o.name.lower(): o for o in RiskOwner.objects.all()}
    
    for p in processes:
        print(f"Checking Process {p.id}: {p.name}")
        
        # We use raw SQL for history to avoid type casting issues if Django tries to cast string to int
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT owner_id FROM risk_universe_historicalprocess WHERE id = %s ORDER BY history_date DESC", 
                [p.id]
            )
            rows = cursor.fetchall()
            
        found_owner_name = None
        for row in rows:
            val = row[0] # owner_id column
            if val and isinstance(val, str) and val.strip():
                found_owner_name = val
                break
            # checking if it is an int that looks like a string? SQLite returns string if it stored string.
        
        if found_owner_name:
            print(f"  Found historical owner: {found_owner_name}")
            
            # Find or Create RiskOwner
            owner_obj = owners_map.get(found_owner_name.lower())
            if not owner_obj:
                print(f"  Creating new RiskOwner: {found_owner_name}")
                owner_obj = RiskOwner.objects.create(name=found_owner_name)
                owners_map[found_owner_name.lower()] = owner_obj
            
            p.owner = owner_obj
            p.save()
            print(f"  Linked to {owner_obj}")
            count += 1
        else:
            print("  No string owner found in history.")

    print(f"Recovery complete. Updated {count} processes.")

if __name__ == "__main__":
    recover()
