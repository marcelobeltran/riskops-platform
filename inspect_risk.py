import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from risk_universe.models import Risk

print("--- Risk Fields ---")
for field in Risk._meta.get_fields():
    print(field.name)
print("-------------------")
