
from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.views import  commandes_utilisateurs
from . import views
from shop.views import register_view



urlpatterns = [
    # Ici tu mettras les routes spécifiques à accounts plus tard
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('register/', register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('commandes-utilisateurs/', commandes_utilisateurs, name='commandes_utilisateurs'),
    path('modifier-photo/', views.modifier_photo_profil, name='modifier_photo_profil'),

]
