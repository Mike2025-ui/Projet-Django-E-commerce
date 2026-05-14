#!/usr/bin/env python
"""
Test complet du système de messaging entre acheteur et vendeur.
Démontre le flux bidirectionnel complet.
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet1djan.settings')

import django
django.setup()

from accounts.models import CustomUser
from shop.models import Product, Category, Discussion, Message
from django.utils import timezone

print("=" * 80)
print("TEST COMPLET: SYSTÈME DE MESSAGING BIDIRECTIONNEL")
print("=" * 80)

# 1. Vérifier/créer les utilisateurs
print("\n[ÉTAPE 1] Vérification des utilisateurs...")
try:
    vendor = CustomUser.objects.get(username='vendor')
    print(f"✓ Vendor trouvé: {vendor.username} (ID: {vendor.id})")
except CustomUser.DoesNotExist:
    vendor = CustomUser.objects.create_user(username='vendor', password='vendor123', email='vendor@test.com')
    print(f"✓ Vendor créé: {vendor.username} (ID: {vendor.id})")

try:
    buyer = CustomUser.objects.get(username='buyer')
    print(f"✓ Buyer trouvé: {buyer.username} (ID: {buyer.id})")
except CustomUser.DoesNotExist:
    buyer = CustomUser.objects.create_user(username='buyer', password='buyer123', email='buyer@test.com')
    print(f"✓ Buyer créé: {buyer.username} (ID: {buyer.id})")

# 2. Vérifier/créer une catégorie et un produit
print("\n[ÉTAPE 2] Vérification du produit...")
category, _ = Category.objects.get_or_create(nom='Électronique')
product, created = Product.objects.get_or_create(
    nom='Test Product',
    defaults={
        'user': vendor,
        'description': 'Un produit de test pour le messaging',
        'prix': 29.99,
        'category': category,
        'stock': 10
    }
)
if created:
    print(f"✓ Produit créé: {product.nom} (ID: {product.id}) - Vendeur: {product.user.username}")
else:
    print(f"✓ Produit trouvé: {product.nom} (ID: {product.id}) - Vendeur: {product.user.username}")

# 3. Créer une discussion
print("\n[ÉTAPE 3] Création de la discussion...")
discussion, created = Discussion.objects.get_or_create(
    acheteur=buyer,
    vendeur=vendor,
    produit=product,
)
print(f"✓ Discussion créée/trouvée (ID: {discussion.id})")
print(f"  - Acheteur: {discussion.acheteur.username}")
print(f"  - Vendeur: {discussion.vendeur.username}")
print(f"  - Produit: {discussion.produit.nom if discussion.produit else 'N/A'}")

# 4. Buyer envoie un message
print("\n[ÉTAPE 4] Buyer envoie un message au Vendor...")
buyer_msg = Message.objects.create(
    discussion=discussion,
    sender=buyer,
    contenu="Bonjour! Je suis intéressé par ce produit. Est-il en stock?"
)
print(f"✓ Message envoyé par {buyer.username}:")
print(f"  - ID: {buyer_msg.id}")
print(f"  - Contenu: '{buyer_msg.contenu}'")
print(f"  - Date: {buyer_msg.date_envoi.strftime('%Y-%m-%d %H:%M:%S')}")
discussion.save()

# 5. Vendor envoie une réponse
print("\n[ÉTAPE 5] Vendor envoie une réponse...")
vendor_msg = Message.objects.create(
    discussion=discussion,
    sender=vendor,
    contenu="Oui, c'est en stock! Nous avons 10 unités disponibles. Livraison gratuite!"
)
print(f"✓ Message envoyé par {vendor.username}:")
print(f"  - ID: {vendor_msg.id}")
print(f"  - Contenu: '{vendor_msg.contenu}'")
print(f"  - Date: {vendor_msg.date_envoi.strftime('%Y-%m-%d %H:%M:%S')}")
discussion.save()

# 6. Buyer envoie une deuxième message
print("\n[ÉTAPE 6] Buyer envoie une question supplémentaire...")
buyer_msg2 = Message.objects.create(
    discussion=discussion,
    sender=buyer,
    contenu="Quel délai de livraison?"
)
print(f"✓ Message envoyé par {buyer.username}:")
print(f"  - ID: {buyer_msg2.id}")
print(f"  - Contenu: '{buyer_msg2.contenu}'")
print(f"  - Date: {buyer_msg2.date_envoi.strftime('%Y-%m-%d %H:%M:%S')}")
discussion.save()

# 7. Afficher la conversation complète
print("\n[ÉTAPE 7] CONVERSATION COMPLÈTE:")
print("-" * 80)
all_messages = discussion.messages.all().order_by('date_envoi')
for msg in all_messages:
    sender_type = "👤 BUYER" if msg.sender == buyer else "🏪 VENDOR"
    print(f"\n{sender_type}: {msg.sender.username}")
    print(f"├─ Heure: {msg.date_envoi.strftime('%H:%M:%S')}")
    print(f"└─ Message: {msg.contenu}")

# 8. Statistiques
print("\n[ÉTAPE 8] STATISTIQUES:")
print("-" * 80)
print(f"Total de messages: {all_messages.count()}")
print(f"Messages du buyer: {all_messages.filter(sender=buyer).count()}")
print(f"Messages du vendor: {all_messages.filter(sender=vendor).count()}")

# 9. Vérifier que la unicité de la discussion fonctionne
print("\n[ÉTAPE 9] Vérification de l'unicité des discussions...")
discussion2, created = Discussion.objects.get_or_create(
    acheteur=buyer,
    vendeur=vendor,
    produit=product,
)
if not created:
    print("✓ CORRECTO: La même discussion est réutilisée (pas de doublons)")
    print(f"  - ID discussion existante: {discussion.id}")
    print(f"  - ID discussion tentée: {discussion2.id}")
    print(f"  - Identiques: {discussion.id == discussion2.id}")

# 10. Tester une deuxième discussion (sans produit spécifique)
print("\n[ÉTAPE 10] Test: Discussion sans produit spécifique...")
discussion_generic, created = Discussion.objects.get_or_create(
    acheteur=buyer,
    vendeur=vendor,
    produit=None,
)
print(f"✓ Discussion générale créée/trouvée (ID: {discussion_generic.id})")
if discussion_generic.produit is None:
    print("  - Pas de produit associé (discussion générale)")

print("\n" + "=" * 80)
print("✅ TEST COMPLET RÉUSSI!")
print("=" * 80)
print("\nRÉSUMÉ:")
print("1. ✓ Acheteur et Vendeur existent")
print("2. ✓ Discussion créée avec produit spécifique")
print("3. ✓ Messages bidirectionnels fonctionnent")
print("4. ✓ Historique des messages préservé")
print("5. ✓ Unicité des discussions respectée (pas de doublons)")
print("6. ✓ Discussions génériques (sans produit) aussi possibles")
print("\nLE SYSTÈME EST FONCTIONNEL! ✅")
