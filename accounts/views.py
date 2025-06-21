from datetime import timedelta, timezone
from django import forms
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from shop.models import Commande  # adapte l'import si besoin
from accounts.models import CustomUser  # adapte si besoin
from django.contrib.auth.decorators import login_required, user_passes_test

from accounts.models import CustomUser
from shop.models import Commande, Product
from .forms import CustomUserCreationForm, ProductForm  # Ton formulaire personnalisé



# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirige s'il est déjà connecté

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html', {'user': request.user})

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
            return redirect('mes_produits')  # ou autre page de redirection
    else:
        form = ProductForm(instance=produit)

    return render(request, 'shop/modifier_produit.html', {'form': form})

def utilisateurs_recents(request):
    temps_limite = timezone.now() - timedelta(minutes=5)
    utilisateurs_en_ligne = CustomUser.objects.filter(last_activity__gte=temps_limite)
    return render(request, 'dashboard/utilisateurs_recents.html', {
        'utilisateurs_en_ligne': utilisateurs_en_ligne
    })

def imprimer_commandes(request):
    # Ici on récupère toutes les commandes de l'utilisateur connecté
    commandes = Commande.objects.filter(utilisateur=request.user)  # ou autre filtre selon ta structure
    
    return render(request, 'accounts/imprimer_commandes.html', {
        'commandes': commandes,
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)  # accès réservé aux admins
def commandes_utilisateurs(request):
    commandes = Commande.objects.select_related('utilisateur').all()
    return render(request, 'accounts/commandes_utilisateurs.html', {
        'commandes': commandes,
    })    

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def modifier_photo_profil(request):
    if request.method == "POST" and request.FILES.get("photo"):
        user = request.user
        user.photo = request.FILES["photo"]
        user.save()
    return redirect('dashboard')