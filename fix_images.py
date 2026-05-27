#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet1djan.settings")
django.setup()

from shop.models import Product
from django.conf import settings

# Nettoyer les produits avec images invalides
for product in Product.objects.all():
    cleaned = False

    # Vérifier si le fichier image existe
    if product.image:
        image_path = os.path.join(settings.MEDIA_ROOT, str(product.image))
        if not os.path.exists(image_path):
            print(f"❌ Image manquante pour '{product.nom}': {product.image}")
            product.image = None
            cleaned = True

    # Si pas d'image locale, mais une URL valide, c'est OK
    if not product.image and not product.image_url:
        print(f"⚠️ Pas d'image pour '{product.nom}' - utilisera l'image par défaut")

    if cleaned:
        product.save()
        print(f"✅ Corrigé: {product.nom}")
    else:
        print(f"✓ OK: {product.nom}")

print("\n✅ Images nettoyées !")
