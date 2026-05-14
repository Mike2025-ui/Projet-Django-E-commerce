from django.contrib import admin
from .models import Category, Product, Commande, LigneCommande, Review, Discussion, Message

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_ajouter')
    search_fields = ('nom',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'stock', 'category', 'date_ajouter')
    list_filter = ('category', 'date_ajouter')
    search_fields = ('nom',)

class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'email', 'date_commande', 'prix_total', 'paye')
    list_filter = ('paye', 'date_commande')

class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('acheteur', 'vendeur', 'produit', 'date_creation', 'date_update')
    list_filter = ('date_creation', 'date_update')
    search_fields = ('acheteur__username', 'vendeur__username')

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'discussion', 'date_envoi')
    list_filter = ('date_envoi',)
    search_fields = ('sender__username', 'contenu')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(LigneCommande)
admin.site.register(Review)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Message, MessageAdmin)