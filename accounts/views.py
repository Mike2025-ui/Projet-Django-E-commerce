import csv
from io import BytesIO
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

from .models import CustomUser
from shop.models import Commande, LigneCommande, Product
from .forms import CustomUserCreationForm, ProductForm


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Identifiants invalides.")
    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.user = request.user
            produit.save()
            messages.success(request, "Produit ajouté avec succès.")
            return redirect("dashboard")
        else:
            messages.error(request, "Erreur dans le formulaire.")
    else:
        form = ProductForm()
    mes_produits = Product.objects.filter(user=request.user)
    return render(
        request,
        "accounts/dashboard.html",
        {
            "form": form,
            "mes_produits": mes_produits,
        },
    )


@login_required
def modifier_photo_profil(request):
    if request.method == "POST" and request.FILES.get("photo"):
        request.user.photo = request.FILES["photo"]
        request.user.save()
    return redirect("dashboard")


from django.contrib.auth.decorators import login_required


@login_required
def commandes_reçues(request):
    statut_filtre = request.GET.get("statut", "")
    commandes = (
        Commande.objects.filter(lignes__produit__user=request.user)
        .distinct()
        .order_by("-date_commande")
    )
    if statut_filtre == "payee":
        commandes = commandes.filter(paye=True)
    elif statut_filtre == "nonpayee":
        commandes = commandes.filter(paye=False)
    return render(
        request,
        "accounts/commandes_reçues.html",
        {"commandes": commandes, "statut_filtre": statut_filtre},
    )


@login_required
def export_commandes_reçues(request):
    lignes = LigneCommande.objects.filter(produit__user=request.user).select_related(
        "commande", "produit"
    )
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = 'attachment; filename="commandes.csv"'
    writer = csv.writer(response, delimiter=";")
    writer.writerow(
        [
            "Produit",
            "Client",
            "Email",
            "Quantité",
            "Prix unitaire",
            "Total",
            "Date",
            "Statut",
        ]
    )
    for l in lignes:
        statut_filtre = request.GET.get("statut")
        if statut_filtre == "payee" and not l.commande.paye:
            continue
        if statut_filtre == "nonpayee" and l.commande.paye:
            continue
        client = (
            l.commande.utilisateur.username
            if l.commande.utilisateur
            else l.commande.nom
        )
        email = (
            l.commande.utilisateur.email if l.commande.utilisateur else l.commande.email
        )
        writer.writerow(
            [
                l.produit.nom,
                client,
                email,
                l.quantite,
                l.prix_unitaire,
                float(l.quantite) * float(l.prix_unitaire),
                l.commande.date_commande.strftime("%d/%m/%Y"),
                "Payée" if l.commande.paye else "Non payée",
            ]
        )
    return response


@login_required
def export_commandes_reçues_pdf(request):
    lignes = LigneCommande.objects.filter(produit__user=request.user).select_related(
        "commande", "produit"
    )
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Commandes reçues")
    y -= 30
    grouped = defaultdict(list)
    for l in lignes:
        statut_filtre = request.GET.get("statut")
        if statut_filtre == "payee" and not l.commande.paye:
            continue
        if statut_filtre == "nonpayee" and l.commande.paye:
            continue
        grouped[l.commande].append(l)
    p.setFont("Helvetica", 10)
    for commande, items in grouped.items():
        if y < 100:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 10)
        client = commande.utilisateur.username if commande.utilisateur else commande.nom
        p.drawString(
            50,
            y,
            f"Client: {client} - {commande.date_commande.strftime('%d/%m/%Y')} - {'Payée' if commande.paye else 'Non payée'}",
        )
        y -= 20
        for item in items:
            total = float(item.quantite) * float(item.prix_unitaire)
            p.drawString(
                60, y, f"{item.produit.nom[:30]} x{item.quantite} = {total:.0f} FCFA"
            )
            y -= 15
        y -= 10
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")


@login_required
def supprimer_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    if request.method == "POST":
        commande.delete()
        messages.success(request, "Commande supprimée.")
    return redirect("commandes_reçues")


@login_required
@user_passes_test(lambda u: u.is_superuser)
def commandes_utilisateurs(request):
    commandes = Commande.objects.select_related("utilisateur").all()
    return render(
        request, "accounts/commandes_utilisateurs.html", {"commandes": commandes}
    )
