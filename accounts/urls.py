from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('modifier-photo/', views.modifier_photo_profil, name='modifier_photo_profil'),
    path('commandes-reçues/', views.commandes_reçues, name='commandes_reçues'),
    path('export-commandes-csv/', views.export_commandes_reçues, name='export_commandes_reçues'),
    path('export-commandes-pdf/', views.export_commandes_reçues_pdf, name='export_commandes_reçues_pdf'),
    path('commande/supprimer/<int:commande_id>/', views.supprimer_commande, name='supprimer_commande'),
    path('commandes-utilisateurs/', views.commandes_utilisateurs, name='commandes_utilisateurs'),
]