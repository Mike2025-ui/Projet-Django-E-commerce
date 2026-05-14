from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('<int:myid>/', views.detail, name='detail'),
    path('paiement/', views.paiement, name='paiement'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('ajouter-panier-api/', views.ajouter_panier_api, name='ajouter_panier_api'),
    path('retirer-panier-api/', views.retirer_panier_api, name='retirer_panier_api'),
    path('get-panier-info/', views.get_panier_info, name='get_panier_info'),
    path('ajouter-produit/', views.ajouter_produit, name='ajouter_produit'),
    path('mes-produits/', views.mes_produits, name='mes_produits'),
    path('modifier-produit/<int:pk>/', views.modifier_produit, name='modifier_produit'),
    path('supprimer-produit/<int:pk>/', views.supprimer_produit, name='supprimer_produit'),
    path('discussion/<int:vendeur_id>/', views.discussion, name='discussion'),
    path('discussion/<int:vendeur_id>/produit/<int:produit_id>/', views.discussion, name='discussion_produit'),
    path('categories/', views.toutes_categories, name='toutes_categories'),
    path('ajouter-categorie/', views.ajouter_categorie, name='ajouter_categorie'),
]