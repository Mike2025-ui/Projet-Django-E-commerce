from django.contrib.auth.decorators import login_required


# Messagerie vendeur : liste toutes les discussions où l'utilisateur est vendeur
@login_required
def messagerie_vendeur(request):
    discussions = (
        request.user.discussions_vendeur.select_related("acheteur", "produit")
        .all()
        .order_by("-date_update")
    )
    return render(request, "shop/messagerie_vendeur.html", {"discussions": discussions})


from .models import Commande

# Suppression d'une commande avec confirmation
from django.contrib.auth.decorators import login_required


@login_required
def supprimer_commande(request, id):
    commande = get_object_or_404(Commande, id=id, utilisateur=request.user)
    if request.method == "POST":
        commande.delete()
        return redirect("commandes_reçues")
    return render(request, "shop/confirmer_suppression.html", {"produit": commande})


import json
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import (
    Product,
    Commande,
    Review,
    LigneCommande,
    Discussion,
    Message,
    Category,
)
from accounts.forms import ProductForm


def index(request):
    item_name = request.GET.get("item_name")
    category = request.GET.get("category")
    product_object = Product.objects.all().order_by("-date_ajouter")
    if item_name:
        product_object = product_object.filter(nom__icontains=item_name)
    if category and category != "Toutes":
        product_object = product_object.filter(category__nom=category)
    paginator = Paginator(product_object, 8)
    page = request.GET.get("page")
    product_object = paginator.get_page(page)
    return render(request, "shop/index.html", {"product_object": product_object})


def detail(request, myid):
    product = get_object_or_404(Product, id=myid)
    reviews = []
    existing_review = None
    return render(
        request,
        "shop/detail.html",
        {"product": product, "reviews": reviews, "existing_review": existing_review},
    )


def paiement(request):
    if request.method == "POST":
        try:
            panier_json = request.POST.get("panier")
            nom = request.POST.get("nom")
            email = request.POST.get("email")
            telephone = request.POST.get("telephone", "")
            adresse = request.POST.get("address")
            ville = request.POST.get("ville")
            pays = request.POST.get("pays")
            code_postal = request.POST.get("zipcode")

            try:
                panier_dict = json.loads(panier_json) if panier_json else {}
            except Exception as e:
                panier_dict = {}

            # Convertir le panier en liste avec calcul du total
            prix_total = 0
            panier_items = []

            if isinstance(panier_dict, dict):
                for pid, item in panier_dict.items():
                    quantite = item.get("quantite", 1)
                    prix_unitaire = float(item.get("prix_unitaire", 0))
                    prix_total += quantite * prix_unitaire
                    panier_items.append(
                        {
                            "produit_id": int(pid),
                            "quantite": quantite,
                            "prix_unitaire": prix_unitaire,
                        }
                    )

            # Créer la commande
            commande = Commande.objects.create(
                utilisateur=request.user if request.user.is_authenticated else None,
                nom=nom,
                email=email,
                telephone=telephone,
                adresse=adresse,
                ville=ville,
                pays=pays,
                code_postal=code_postal,
                prix_total=prix_total,
                paye=False,
            )

            # Créer les lignes de commande
            for item in panier_items:
                try:
                    produit = Product.objects.get(id=item["produit_id"])
                    LigneCommande.objects.create(
                        commande=commande,
                        produit=produit,
                        quantite=item["quantite"],
                        prix_unitaire=item["prix_unitaire"],
                    )
                except Product.DoesNotExist:
                    pass

            # Vider le panier de la session et envoyer le SMS
            request.session["panier"] = {}
            request.session.modified = True
            send_confirmation_email(nom, telephone, prix_total, commande.id, commande)

            return render(
                request,
                "shop/confirmation.html",
                {
                    "nom": nom,
                    "email": email,
                    "telephone": telephone,
                    "prix_total": prix_total,
                    "payer": False,
                    "commande_id": commande.id,
                },
            )
        except Exception as e:
            import traceback

            error_details = traceback.format_exc()
            return render(
                request,
                "shop/panier.html",
                {
                    "erreur": f"Erreur lors de la création de la commande : {str(e)}",
                    "details_erreur": error_details,
                },
                status=500,
            )
    return render(request, "shop/panier.html")


def confirmation(request):
    # Récupérer le dernier message de confirmation
    return render(request, "shop/confirmation.html")


def send_confirmation_email(nom, numero_tel, prix_total, commande_id, commande=None):
    """Envoyer un SMS de confirmation au lieu d'un email"""
    from .models import SMS

    # Format du message SMS
    message_sms = f"Bonjour {nom}, votre commande n°{commande_id} de {prix_total} FCFA est confirmée. Merci !"

    statut_sms = "en_attente"
    message_id = None

    try:
        # Si Twilio est configuré, envoyer via Twilio
        twilio_account = getattr(settings, "TWILIO_ACCOUNT_SID", None)
        twilio_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
        twilio_phone = getattr(settings, "TWILIO_PHONE", None)

        if twilio_account and twilio_token and twilio_phone:
            from twilio.rest import Client

            client = Client(twilio_account, twilio_token)
            message = client.messages.create(
                body=message_sms,
                from_=twilio_phone,
                to=numero_tel,
            )
            print(f"✅ SMS envoyé avec succès: {message.sid}")
            statut_sms = "envoyé"
            message_id = message.sid
        else:
            print(f"📱 SMS à envoyer à {numero_tel}: {message_sms}")
            statut_sms = "envoyé"
    except Exception as e:
        # En développement, ignorer les erreurs d'SMS
        print(f"⚠️ Erreur lors de l'envoi du SMS : {str(e)}")
        statut_sms = "erreur"

    # Enregistrer le SMS en base de données
    try:
        SMS.objects.create(
            commande=commande,
            numero_destinataire=numero_tel,
            contenu=message_sms,
            statut=statut_sms,
            message_id=message_id,
        )
    except Exception as e:
        print(f"⚠️ Erreur lors de l'enregistrement du SMS : {str(e)}")


@require_http_methods(["POST"])
def ajouter_panier_api(request):
    product_id = request.POST.get("product_id")
    try:
        produit = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Produit introuvable"}, status=404)
    panier = request.session.get("panier", {})
    pid = str(product_id)
    if pid in panier:
        panier[pid]["quantite"] += 1
    else:
        panier[pid] = {
            "quantite": 1,
            "nom": produit.nom,
            "prix_unitaire": float(produit.prix),
        }
    request.session["panier"] = panier
    return JsonResponse({"success": True})


@require_http_methods(["POST"])
def retirer_panier_api(request):
    product_id = request.POST.get("product_id")
    panier = request.session.get("panier", {})
    pid = str(product_id)
    if pid in panier:
        if panier[pid]["quantite"] > 1:
            panier[pid]["quantite"] -= 1
        else:
            del panier[pid]
        request.session["panier"] = panier
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Non présent"}, status=400)


def get_panier_info(request):
    panier = request.session.get("panier", {})
    total = 0
    quantite_totale = 0
    for item in panier.values():
        q = item["quantite"]
        prix = item["prix_unitaire"]
        total += q * prix
        quantite_totale += q
    return JsonResponse(
        {"panier": panier, "total": total, "quantite_totale": quantite_totale}
    )


@login_required
def ajouter_produit(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.user = request.user
            produit.save()
            return redirect("mes_produits")
    else:
        form = ProductForm()
    return render(request, "shop/ajouter_produit.html", {"form": form})


@login_required
def mes_produits(request):
    produits = Product.objects.filter(user=request.user)
    return render(request, "accounts/mes_produits.html", {"produits": produits})


@login_required
def modifier_produit(request, pk):
    produit = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            return redirect("mes_produits")
    else:
        form = ProductForm(instance=produit)
    return render(
        request, "shop/modifier_produit.html", {"form": form, "produit": produit}
    )


@login_required
def supprimer_produit(request, pk):
    produit = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == "POST":
        produit.delete()
        return redirect("mes_produits")
    return render(request, "shop/confirmer_suppression.html", {"produit": produit})


@login_required
@login_required
def discussion(request, vendeur_id, produit_id=None):
    """Page de discussion avec un vendeur"""
    from accounts.models import CustomUser

    vendeur = get_object_or_404(CustomUser, id=vendeur_id)
    produit = None
    if produit_id:
        produit = get_object_or_404(Product, id=produit_id)

    # Créer ou récupérer la discussion
    discussion_obj, created = Discussion.objects.get_or_create(
        acheteur=request.user, vendeur=vendeur, produit=produit
    )

    if request.method == "POST":
        contenu = request.POST.get("contenu", "").strip()
        if contenu:
            Message.objects.create(
                discussion=discussion_obj, sender=request.user, contenu=contenu
            )
            discussion_obj.save()  # Mise à jour du date_update
            # Pas de message de confirmation
            if produit_id:
                return redirect(
                    "discussion_produit", vendeur_id=vendeur_id, produit_id=produit_id
                )
            else:
                return redirect("discussion", vendeur_id=vendeur_id)
        else:
            messages.error(request, "Le message ne peut pas être vide.")

    messages_list = discussion_obj.messages.all()
    return render(
        request,
        "shop/discussion.html",
        {
            "discussion": discussion_obj,
            "messages": messages_list,
            "vendeur": vendeur,
            "produit": produit,
        },
    )


def toutes_categories(request):
    """Afficher toutes les catégories et permettre d'en ajouter une nouvelle"""
    categories = Category.objects.all().order_by("-date_ajouter")
    paginator = Paginator(categories, 12)
    page = request.GET.get("page")
    categories = paginator.get_page(page)
    return render(request, "shop/toutes_categories.html", {"categories": categories})


@login_required
def ajouter_categorie(request):
    """Ajouter une nouvelle catégorie"""
    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        if nom and len(nom) >= 2:
            # Vérifier si la catégorie existe déjà
            if not Category.objects.filter(nom__iexact=nom).exists():
                Category.objects.create(nom=nom)
                messages.success(request, f'Catégorie "{nom}" ajoutée avec succès!')
                return redirect("toutes_categories")
            else:
                messages.warning(request, f'La catégorie "{nom}" existe déjà.')
        else:
            messages.error(
                request, "Le nom de la catégorie doit contenir au moins 2 caractères."
            )
    return render(request, "shop/ajouter_categorie.html")
