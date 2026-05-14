# 🎬 GUIDE ÉTAPE PAR ÉTAPE - Voir le Système en Action

## 📺 Démonstration Interactive

Ce guide vous montrera comment le système de messaging fonctionne en action.

---

## 🎯 Scénario: Acheteur achète un produit et discute avec le vendeur

### ÉTAPE 1️⃣: Démarrer le Serveur

```bash
cd c:\Users\TOSHIBA\Desktop\Projet\ Django\Projet-Django-E-commerce
python manage.py runserver
```

**Résultat attendu:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### ÉTAPE 2️⃣: Vérifier que les données de test existent

```bash
# Dans un autre terminal:
python test_messaging_flow.py
```

**Résultat:** ✅ TEST COMPLET RÉUSSI (voir screenshot)

---

### 👤 PREMIER UTILISATEUR: BUYER (ACHETEUR)

#### ÉTAPE 3️⃣: Ouvrir le navigateur et aller à la page d'accueil

```
http://localhost:8000/
```

**Vous verrez:**
- Logo "Shop-in-Line"
- Liste des produits
- "Test Product" dans la liste

#### ÉTAPE 4️⃣: Cliquer sur "Test Product"

**Page actuelle:** Page d'accueil
**Action:** Cliquer sur le produit "Test Product"
**URL résultante:** `http://localhost:8000/shop/produit/4/`

**Vous verrez:**
- Détails du produit
- Prix: 29.99€
- Bouton "Contacter le vendeur" (🟢 FIXÉ)

#### ÉTAPE 5️⃣: Cliquer "Contacter le Vendeur"

**Page actuelle:** Détail produit
**Action:** Cliquer le bouton "Contacter le vendeur"
**URL résultante:** `http://localhost:8000/discussion/4/produit/4/`

**Important:**
- 4 = ID du vendeur
- 4 = ID du produit
- URL includes **both** parameters (c'était le bug!)

**Vous verrez:**
- En-tête: "Discussion avec vendor"
- Sous-titre: "Produit: Test Product"
- Zone des messages (vide pour la première fois)
- Champ de saisie pour écrire un message

#### ÉTAPE 6️⃣: Écrire et Envoyer un Message

**Page actuelle:** Page discussion
**Action:**
1. Cliquez dans le champ de saisie
2. Tapez: `Bonjour! Avez-vous ce produit en stock?`
3. Cliquez "Envoyer"

**Résultat:**
- ✅ Alerte "Message envoyé avec succès!"
- ✅ Page se recharge
- ✅ Votre message s'affiche en **BLEU À DROITE**
- ✅ Heure d'envoi: 09:15

**Screenshot (Votre Vue):**
```
┌──────────────────────────────────────────┐
│ 📱 Discussion avec vendor                │
│ Produit: Test Product                    │
├──────────────────────────────────────────┤
│                                          │
│                  ┌─ ─ ─ ─ ─ ─ ─ ─┐      │
│                  │ Bonjour!      │ 🟦   │
│                  │ Avez-vous...? │      │
│                  │        09:15  │      │
│                  └─ ─ ─ ─ ─ ─ ─ ─┘      │
│                                          │
│  [Champ de saisie...           ] [Envoy]│
└──────────────────────────────────────────┘
```

---

### 🏪 DEUXIÈME UTILISATEUR: VENDOR (VENDEUR)

#### ÉTAPE 7️⃣: Se Déconnecter

**Page actuelle:** Discussion (buyer)
**Action:** Cliquez l'avatar utilisateur (en haut à droite) → "Logout"

**Résultat:**
- ✅ Déconnexion réussie
- ✅ Redirect à la page d'accueil
- ✅ Navbar montre "Se connecter"

#### ÉTAPE 8️⃣: Se Reconnecter comme VENDOR

**Page actuelle:** Page d'accueil (non authentifié)
**Action:** Cliquez "Se connecter"
**URL:** `http://localhost:8000/accounts/login/`

**Formulaire de connexion:**
- Nom d'utilisateur: `vendor`
- Mot de passe: `vendor123`
- Cliquez "Se connecter"

**Résultat:**
- ✅ Login réussi
- ✅ Redirect à la page d'accueil
- ✅ Navbar montre "vendor" en haut

#### ÉTAPE 9️⃣: Naviguer à la Discussion

**Page actuelle:** Page d'accueil (authentifié comme vendor)
**Action:** Naviguez à l'URL manuellement

```
http://localhost:8000/discussion/5/produit/4/
```

**Explication des paramètres:**
- 5 = ID du buyer (l'acheteur qui a envoyé le message)
- 4 = ID du produit

**Vous verrez (Vue Vendor):**
- En-tête: "Discussion avec buyer"
- Votre message **reçu** en **GRIS À GAUCHE**
- Champ de saisie pour répondre

**Screenshot (Vue Vendor):**
```
┌──────────────────────────────────────────┐
│ 📱 Discussion avec buyer                 │
│ Produit: Test Product                    │
├──────────────────────────────────────────┤
│                                          │
│  ┌─ ─ ─ ─ ─ ─ ─ ─┐                      │
│  │ buyer          │                      │
│  │ Bonjour!       │ 🟫                   │
│  │ Avez-vous...?  │                      │
│  │        09:15   │                      │
│  └─ ─ ─ ─ ─ ─ ─ ─┘                      │
│                                          │
│  [Champ de saisie...           ] [Envoy]│
└──────────────────────────────────────────┘
```

#### ÉTAPE 1️⃣0️⃣: Vendor Répond au Message

**Page actuelle:** Discussion (vendor)
**Action:**
1. Cliquez dans le champ de saisie
2. Tapez: `Oui, nous en avons 5 en stock! Livraison gratuite.`
3. Cliquez "Envoyer"

**Résultat:**
- ✅ Alerte "Message envoyé avec succès!"
- ✅ Page se recharge
- ✅ Votre message (vendor) s'affiche en **BLEU À DROITE**
- ✅ Le message précédent du buyer s'affiche en **GRIS À GAUCHE**

**Screenshot (Vue Vendor Après Réponse):**
```
┌──────────────────────────────────────────┐
│ 📱 Discussion avec buyer                 │
│ Produit: Test Product                    │
├──────────────────────────────────────────┤
│                                          │
│  ┌─ ─ ─ ─ ─ ─ ─ ─┐                      │
│  │ buyer          │                      │
│  │ Bonjour!       │ 🟫                   │
│  │ Avez-vous...?  │                      │
│  │        09:15   │                      │
│  └─ ─ ─ ─ ─ ─ ─ ─┘                      │
│                                          │
│              ┌─ ─ ─ ─ ─ ─ ─ ─┐          │
│              │ Oui, 5 en  │ 🟦          │
│              │ stock!     │             │
│              │ Livraison  │             │
│              │ gratuite   │             │
│              │     09:20  │             │
│              └─ ─ ─ ─ ─ ─ ─ ─┘          │
│                                          │
│  [Champ de saisie...           ] [Envoy]│
└──────────────────────────────────────────┘
```

---

### 👤 DE RETOUR: BUYER REÇOIT LA RÉPONSE

#### ÉTAPE 1️⃣1️⃣: Se Reconnecter comme BUYER

**Répétez ÉTAPE 7️⃣ (Logout) et ÉTAPE 8️⃣ (Login)**

Cette fois:
- Nom d'utilisateur: `buyer`
- Mot de passe: `buyer123`

#### ÉTAPE 1️⃣2️⃣: Retourner à la Discussion

**Page actuelle:** Page d'accueil (authentifié comme buyer)
**Action:** Naviguez à l'URL

```
http://localhost:8000/discussion/4/produit/4/
```

**Explication:**
- 4 = ID du vendor (le vendeur)
- 4 = ID du produit

**Résultat: Buyer Voit la Réponse du Vendor! ✅**

**Screenshot (Vue Buyer Reçoit Réponse):**
```
┌──────────────────────────────────────────┐
│ 📱 Discussion avec vendor                │
│ Produit: Test Product                    │
├──────────────────────────────────────────┤
│                                          │
│              ┌─ ─ ─ ─ ─ ─ ─ ─┐          │
│              │ Bonjour!      │ 🟦       │
│              │ Avez-vous...? │          │
│              │        09:15  │          │
│              └─ ─ ─ ─ ─ ─ ─ ─┘          │
│                                          │
│  ┌─ ─ ─ ─ ─ ─ ─ ─┐                      │
│  │ vendor         │                      │
│  │ Oui, 5 en      │ 🟫                   │
│  │ stock!         │                      │
│  │ Livraison      │                      │
│  │ gratuite       │                      │
│  │        09:20   │                      │
│  └─ ─ ─ ─ ─ ─ ─ ─┘                      │
│                                          │
│  [Champ de saisie...           ] [Envoy]│
└──────────────────────────────────────────┘
```

#### ÉTAPE 1️⃣3️⃣: Buyer Envoie une Deuxième Question

**Action:** Tapez `Quelle est la date de livraison?` et envoyez

**Résultat:**
- ✅ Votre nouveau message en **BLEU À DROITE**
- ✅ Tous les messages précédents restent
- ✅ Historique complet conservé

---

## 🎓 Ce que Vous Avez Appris

| Concept | Démonstration |
|---------|---|
| **Routing correct** | Contact button → /discussion/4/produit/4/ ✅ |
| **Bidirectionnel** | Buyer envoie → Vendor reçoit → Vendor répond |
| **Couleurs** | Bleu à droite (vous) / Gris à gauche (eux) |
| **Persistance** | Messages restent après rechargement |
| **Unicité** | Même discussion pour buyer + vendor + produit |
| **Timestamps** | Chaque message a une heure |
| **Validation** | Messages vides ignorés, pas d'erreur |

---

## 🔍 Vérifications Supplémentaires

### Vérifier la Base de Données

```bash
python manage.py shell
```

```python
from shop.models import Discussion, Message

# Voir les discussions
for d in Discussion.objects.all():
    print(f"Discussion #{d.id}: {d.acheteur} ↔ {d.vendeur} | Produit: {d.produit}")
    print(f"  Messages: {d.messages.count()}")

# Voir les messages
for m in Message.objects.all():
    print(f"Message #{m.id}: {m.sender} → {m.contenu[:50]}...")
```

**Résultat attendu:**
```
Discussion #4: buyer ↔ vendor | Produit: Test Product
  Messages: 3

Message #6: buyer → Bonjour! Je suis intéressé par ce produit...
Message #7: vendor → Oui, c'est en stock! Nous avons 10 unités...
Message #8: buyer → Quel délai de livraison?
```

### Vérifier les URLs

Testez ces URLs dans le navigateur:

| URL | Expected |
|-----|----------|
| `/` | Page d'accueil avec produits |
| `/shop/produit/4/` | Détail du Test Product |
| `/discussion/4/produit/4/` | Discussion buyer ↔ vendor + produit |
| `/discussion/5/` | Discussion buyer ↔ vendor (générale) |
| `/categories/` | Toutes les catégories |
| `/ajouter-categorie/` | Form pour ajouter catégorie |
| `/accounts/login/` | Page de login |

---

## 🎉 Résultat Final

```
✅ Acheteur navigue un produit
✅ Acheteur clique "Contacter le vendeur"
✅ Acheteur envoie un message
✅ Message s'affiche en BLEU À DROITE
✅ Vendeur se connecte
✅ Vendeur navigue à la discussion
✅ Vendeur voit le message en GRIS À GAUCHE
✅ Vendeur envoie une réponse
✅ Message s'affiche en BLEU À DROITE (vendor POV)
✅ Acheteur se reconnecte
✅ Acheteur voit la réponse en GRIS À GAUCHE
✅ Conversation COMPLÈTE et BIDIRECTIONNELLE!
```

---

## 🚀 Prochaines Étapes Possibles

1. **Ajouter des notifications** - Quand un message arrive
2. **Marquer comme lu** - Tracker messages non lus
3. **Archiver les discussions** - Les garder hors de la vue
4. **Rechercher dans les messages** - Trouver une discussion
5. **Supprimer les messages** - Option delete par message
6. **Partager fichiers** - Upload images/documents

---

**Bon test! 🎬**

Si vous avez des questions ou des problèmes, référez-vous à:
- `MESSAGING_SYSTEM_DOCS.md` - Documentation technique
- `README_SUMMARY.md` - Résumé des changements
- `test_messaging_flow.py` - Script de test
