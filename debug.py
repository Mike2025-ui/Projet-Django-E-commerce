import os
import sys
import django

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet1djan.settings')

# Afficher les infos de debug
print("=== DEBUG DATABASE CONFIGURATION ===")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"RENDER env: {os.environ.get('RENDER')}")

# Essayer d'importer les settings
try:
    django.setup()
    from django.conf import settings
    print(f"DATABASES config: {settings.DATABASES}")
except Exception as e:
    print(f"Erreur: {e}")
    sys.exit(1)