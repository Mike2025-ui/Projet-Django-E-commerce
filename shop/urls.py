from django.urls import path
from accounts import views
from shop.views import index, detail, paiement, confirmation, payer
from .views import commandes_reçues, export_commandes_reçues, export_commandes_reçues_pdf, register_view, dashboard_view
from accounts.views import login_view, logout_view
from django.shortcuts import redirect
from shop.views import ajouter_produit, mes_produits, modifier_produit, supprimer_produit


urlpatterns = [
    # Redirection de la racine vers login (tu peux modifier plus tard)
    path('', lambda request: redirect('login'), name='home'),

    # Ajout de la route index (page d'accueil)
    path('index/', index, name='index'),

    # Produits
    path('<int:myid>/', detail, name='detail'),
    path('paiement/', paiement, name='paiement'),
    path('confirmation/', confirmation, name='confirmation'),
    path('payer/', payer, name='payer'),
    path('paiement/detail/', paiement, name='paiement_detail'),

    # Authentification
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Tableau de bord
    path('dashboard/', dashboard_view, name='dashboard'),

    path('imprimer-commandes/', views.imprimer_commandes, name='imprimer_commandes'),
    path('ajouter-produit/', ajouter_produit, name='ajouter_produit'),
    path('mes-produits/', mes_produits, name='mes_produits'),
    path('mes-produits/supprimer/<int:produit_id>/', supprimer_produit, name='supprimer_produit'),
    path('modifier-produit/<int:produit_id>/', modifier_produit, name='modifier_produit'),
    path('supprimer-produit/<int:produit_id>/', supprimer_produit, name='supprimer_produit'),
    path('commandes-reçues/', commandes_reçues, name='commandes_reçues'),
    # ...existing code...
path('export-commandes-reçues/', export_commandes_reçues, name='export_commandes_reçues'),
# ...existing code...
path('export-commandes-reçues-pdf/', export_commandes_reçues_pdf, name='export_commandes_reçues_pdf'),

]

