from django.contrib import admin
from .models import Category, Product, Commande
from .models import Review
from .models import LigneCommande  # Ajoute cette importation

admin.site.site_header = "Administration de la Boutique"
admin.site.index_title = "Bienvenue dans l'administration de la boutique"

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_ajouter')
    search_fields = ('nom',)
    list_filter = ('date_ajouter',)
    ordering = ('-date_ajouter',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'category', 'date_ajouter', 'image', 'image_url')
    search_fields = ('nom', 'category__nom')
    list_filter = ('date_ajouter',)
    list_editable = ('prix', 'category')
    ordering = ('-date_ajouter',)
    fields = ('nom', 'description', 'prix', 'category', 'image', 'image_url')

class CommandeAdmin(admin.ModelAdmin):
    actions = None
    list_display = (
        'utilisateur', 'nom', 'email', 'adresse', 'ville', 'pays',
        'code_postal', 'date_commande', 'prix_total', 'paye'
    )
    search_fields = ('utilisateur__username', 'nom', 'paye', 'email')
    list_filter = ('date_commande', 'paye', 'ville', 'pays')
    ordering = ('-date_commande',)

# ...existing code...

admin.site.register(LigneCommande) 
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(Review)