from datetime import timedelta, timezone
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from django.db.models import Avg
from accounts.forms import ProductForm
from accounts.forms import CustomUserCreationForm
from accounts.models import CustomUser
from .models import Product, Commande, Category, Review, LigneCommande
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import json
from django.contrib.auth import get_user_model

def categories_processor(request):
    return {'categories_nav': Category.objects.all()}

def index(request):
    item_name = request.GET.get("item_name")
    category = request.GET.get("category")

    product_object = Product.objects.all().order_by("-date_ajouter")

    if item_name:
        product_object = product_object.filter(nom__icontains=item_name)
    if category:
        product_object = product_object.filter(category__nom=category)

    product_object = product_object.annotate(moyenne_note=Avg('reviews__note'))

    paginator = Paginator(product_object, 4)
    page = request.GET.get("page")
    product_object = paginator.get_page(page)

    return render(request, "shop/index.html", {"product_object": product_object})

@login_required
def detail(request, myid):
    product = get_object_or_404(Product, id=myid)
    review_list = Review.objects.filter(product=product).order_by("-date_added")

    paginator = Paginator(review_list, 5)
    page_number = request.GET.get("page")
    reviews = paginator.get_page(page_number)

    existing_review = Review.objects.filter(product=product, user=request.user).first()

    if request.method == 'POST':
        note = int(request.POST.get('note', 5))
        commentaire = request.POST.get('commentaire', '').strip()

        if commentaire:
            if existing_review:
                existing_review.note = note
                existing_review.commentaire = commentaire
                existing_review.save()
            else:
                Review.objects.create(
                    product=product,
                    user=request.user,
                    note=note,
                    commentaire=commentaire
                )
            return redirect('detail', myid=product.id)

    return render(request, "shop/detail.html", {
        "product": product,
        "reviews": reviews,
        "existing_review": existing_review
    })

def paiement(request):
    if request.method == "POST":
        panier_json = request.POST.get("panier")
        nom = request.POST.get("nom")
        email = request.POST.get("email")
        address = request.POST.get("address")
        ville = request.POST.get("ville")
        pays = request.POST.get("pays")
        code_postal = request.POST.get("zipcode")
        prix_total = request.POST.get("prix_total") or "0"

        try:
            panier = json.loads(panier_json)
        except Exception:
            panier = []

        commande = Commande.objects.create(
            utilisateur=request.user if request.user.is_authenticated else None,
            nom=nom,
            email=email,
            adresse=address,
            ville=ville,
            pays=pays,
            code_postal=code_postal,
            prix_total=prix_total,
            paye=False,
        )
        print("PANIER JSON REÇU :", panier_json)
        for item in panier:
            print("PANIER PARSÉ ITEM :", item)
            produit = Product.objects.get(id=item['produit_id'])
            LigneCommande.objects.create(
                commande=commande,
                produit=produit,
                quantite=item['quantite'],
                prix_unitaire=item['prix_unitaire'],
            )

        request.session["paiement_info"] = {"nom": nom, "email": email, "payer": False}
        return redirect("confirmation")

    return render(request, "shop/paiement.html")

def confirmation(request):
    paiement_info = request.session.pop("paiement_info", None)
    nom = ""
    email = ""
    if paiement_info:
        nom = paiement_info.get("nom", "")
        email = paiement_info.get("email", "")
    else:
        commande = Commande.objects.last()
        nom = commande.nom if commande else ""
        email = commande.email if commande else ""

    context = {"nom": nom, "email": email, "payer": False}
    if paiement_info:
        context.update({"payer": paiement_info.get("payer", False)})
    return render(request, "shop/confirmation.html", context)

@csrf_exempt
def payer(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        email = request.POST.get("email")
        adresse = request.POST.get("address")
        ville = request.POST.get("ville")
        pays = request.POST.get("pays")
        code_postal = request.POST.get("zipcode")
        prix_total = request.POST.get("prix_total") or "0"
        panier_json = request.POST.get("panier")

        try:
            panier = json.loads(panier_json)
        except Exception:
            panier = []

        commande = Commande.objects.create(
            utilisateur=request.user if request.user.is_authenticated else None,
            nom=nom,
            email=email,
            adresse=adresse,
            ville=ville,
            pays=pays,
            code_postal=code_postal,
            prix_total=prix_total,
            paye=True,
        )

        print("PANIER JSON REÇU :", request.POST.get("panier"))
        for item in panier:
            print("ITEM :", item)
            produit = Product.objects.get(id=item['produit_id'])
            LigneCommande.objects.create(
                commande=commande,
                produit=produit,
                quantite=item['quantite'],
                prix_unitaire=item['prix_unitaire'],
            )

        return render(
            request,
            "shop/confirmation.html",
            {
                "nom": nom,
                "prix_total": prix_total,
                "payer": True,
            },
        )

    return HttpResponse("Méthode non autorisée", status=405)


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)  # Ajout de request.FILES
        if form.is_valid():
            user = form.save()
            login(request, user)  # Connexion automatique après inscription
            user = get_user_model().objects.get(pk=user.pk)
            return redirect('dashboard')  # Redirection vers le dashboard
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard_view(request):
    mes_produits = Product.objects.filter(user=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.user = request.user
            produit.save()
            messages.success(request, "Produit ajouté avec succès.")
            return redirect('dashboard')
        else:
            messages.error(request, "Erreur dans le formulaire.")
    else:
        form = ProductForm()
    return render(request, 'accounts/dashboard.html', {
        'user': request.user,
        'mes_produits': mes_produits,
        'form': form,
    })
    
@login_required
def commandes_view(request):
    commandes = Commande.objects.filter(utilisateur=request.user)
    return render(request, "shop/commandes.html", {"commandes": commandes})

@login_required
def commande_detail(request, pk):
    commande = get_object_or_404(Commande, pk=pk, utilisateur=request.user)
    return render(request, "shop/commande_detail.html", {"commande": commande})

def ajouter_produit(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.user = request.user
            produit.save()
            return redirect('mes_produits')
    else:
        form = ProductForm()
    return render(request, 'shop/ajouter_produit.html', {'form': form})

@login_required
def mes_produits(request):
    produits = Product.objects.filter(user=request.user)
    return render(request, 'shop/mes_produits.html', {'produits': produits})

def modifier_produit(request, produit_id):
    produit = get_object_or_404(Product, id=produit_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('mes_produits')
    else:
        form = ProductForm(instance=produit)

    return render(request, 'shop/modifier_produit.html', {'form': form})

@login_required
def supprimer_produit(request, produit_id):
    produit = get_object_or_404(Product, id=produit_id, user=request.user)

    if request.method == 'POST':
        produit.delete()
        return redirect('mes_produits')

    return render(request, 'shop/confirmer_suppression.html', {'produit': produit})

def tableau_de_bord(request):
    temps_limite = timezone.now() - timedelta(minutes=5)
    utilisateurs_en_ligne = CustomUser.objects.filter(last_activity__gte=temps_limite)

    mes_produits = Product.objects.filter(user=request.user)
    produits_globaux = Product.objects.all()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.user = request.user
            produit.save()
            messages.success(request, "Produit ajouté avec succès.")
            return redirect('dashboard')
        else:
            messages.error(request, "Erreur dans le formulaire.")
    else:
        form = ProductForm()

    return render(request, 'dashboard/index.html', {
        'utilisateurs_en_ligne': utilisateurs_en_ligne,
        'mes_produits': mes_produits,
        'produits_globaux': produits_globaux,
        'form': form,
    })

@login_required
def commandes_reçues(request):
    lignes = LigneCommande.objects.filter(produit__user=request.user).select_related('commande', 'produit', 'commande__utilisateur')
    # Ajoute le montant total à chaque ligne
    for ligne in lignes:
        ligne.montant_total = ligne.quantite * ligne.prix_unitaire
    return render(request, 'accounts/commandes_reçues.html', {'lignes': lignes})

import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import LigneCommande

@login_required
def export_commandes_reçues(request):
    lignes = LigneCommande.objects.filter(produit__user=request.user).select_related('commande', 'produit', 'commande__utilisateur')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="commandes_reçues.csv"'

    # Pour Excel, utilise le point-virgule comme séparateur
    writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_ALL)

    writer.writerow([
        'Produit', 'Client', 'Email', 'Quantité', 'Prix unitaire', 'Montant total', 'Date', 'Statut'
    ])

    for ligne in lignes:
        if request.GET.get("statut") == "payee" and not ligne.commande.paye:
            continue
        if request.GET.get("statut") == "nonpayee" and ligne.commande.paye:
            continue

        client = ligne.commande.utilisateur.username if ligne.commande.utilisateur else ligne.commande.nom
        email = ligne.commande.utilisateur.email if ligne.commande.utilisateur else ligne.commande.email
        statut = "Payée" if ligne.commande.paye else "Non payée"
        montant = float(ligne.quantite) * float(ligne.prix_unitaire)
        writer.writerow([
            ligne.produit.nom,
            client,
            email,
            ligne.quantite,
            ligne.prix_unitaire,
            montant,
            ligne.commande.date_commande.strftime("%d/%m/%Y %H:%M"),
            statut
        ])

    return response


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def export_commandes_reçues_pdf(request):
    lignes = LigneCommande.objects.filter(produit__user=request.user).select_related('commande', 'produit', 'commande__utilisateur')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Commandes reçues")
    y -= 30

    p.setFont("Helvetica-Bold", 9)
    headers = ["Produit", "Client", "Email", "Quantité", "Prix unitaire", "Montant", "Date", "Statut"]
    x_list = [50, 120, 220, 320, 360, 420, 480, 540]
    for i, header in enumerate(headers):
        p.drawString(x_list[i], y, header)
    y -= 18

    p.setFont("Helvetica", 8)
    for ligne in lignes:
        if request.GET.get("statut") == "payee" and not ligne.commande.paye:
            continue
        if request.GET.get("statut") == "nonpayee" and ligne.commande.paye:
            continue

        client = (ligne.commande.utilisateur.username if ligne.commande.utilisateur else ligne.commande.nom) or ""
        email = (ligne.commande.utilisateur.email if ligne.commande.utilisateur else ligne.commande.email) or ""
        statut = "Payée" if ligne.commande.paye else "Non payée"
        montant = float(ligne.quantite) * float(ligne.prix_unitaire)

        # Tronquer les textes trop longs
        def truncate(text, maxlen):
            return (text[:maxlen-3] + '...') if len(text) > maxlen else text

        data = [
            truncate(str(ligne.produit.nom), 18),
            truncate(str(client), 14),
            truncate(str(email), 22),
            str(ligne.quantite),
            str(ligne.prix_unitaire),
            str(montant),
            ligne.commande.date_commande.strftime("%d/%m/%Y %H:%M"),
            statut
        ]
        for i, value in enumerate(data):
            p.drawString(x_list[i], y, value)
        y -= 15
        if y < 50:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 8)

    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
