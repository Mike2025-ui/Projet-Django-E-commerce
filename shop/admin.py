from django.contrib import admin
from .models import (
    Category,
    Product,
    Commande,
    LigneCommande,
    Review,
    Discussion,
    Message,
    SMS,
)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("nom", "date_ajouter")
    search_fields = ("nom",)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("nom", "prix", "stock", "category", "date_ajouter")
    list_filter = ("category", "date_ajouter")
    search_fields = ("nom",)


class CommandeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nom",
        "telephone",
        "email",
        "date_commande",
        "prix_total",
        "paye",
    )
    list_filter = ("paye", "date_commande")
    search_fields = ("nom", "telephone", "email")


class DiscussionAdmin(admin.ModelAdmin):
    list_display = ("acheteur", "vendeur", "produit", "date_creation", "date_update")
    list_filter = ("date_creation", "date_update")
    search_fields = ("acheteur__username", "vendeur__username")


class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "discussion", "date_envoi")
    list_filter = ("date_envoi",)
    search_fields = ("sender__username", "contenu")


class SMSAdmin(admin.ModelAdmin):
    list_display = ("numero_destinataire", "statut", "date_envoi", "commande")
    list_filter = ("statut", "date_envoi")
    search_fields = ("numero_destinataire", "contenu")
    readonly_fields = ("date_envoi", "message_id")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(LigneCommande)
admin.site.register(Review)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(SMS, SMSAdmin)
