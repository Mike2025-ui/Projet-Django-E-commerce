from django.db import models
from django.conf import settings  # Import pour AUTH_USER_MODEL

class Category(models.Model):
    nom = models.CharField(max_length=200)
    date_ajouter = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_ajouter']

    def __str__(self):
        return self.nom


class Product(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mes_produits",
        verbose_name="Ajouté par"
    )
    nom = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='products'
    )
    image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name="Image locale")
    image_url = models.URLField(blank=True, null=True, verbose_name="Image en ligne")
    date_ajouter = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_ajouter']
        verbose_name_plural = 'Produits'

    def __str__(self):
        return self.nom

    def get_image(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return '/static/img/produit-default.png'



class Commande(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Client",
        null=True,
        blank=True
    )
    nom = models.CharField(max_length=150, verbose_name="Nom complet", null=True, blank=True)
    email = models.EmailField(verbose_name="Adresse email", null=True, blank=True)
    adresse = models.CharField(max_length=255, verbose_name="Adresse de livraison", null=True, blank=True)
    ville = models.CharField(max_length=100, verbose_name="Ville", null=True, blank=True)
    pays = models.CharField(max_length=100, verbose_name="Pays", null=True, blank=True)
    code_postal = models.CharField(max_length=20, verbose_name="Code postal", null=True, blank=True)
    date_commande = models.DateTimeField(auto_now_add=True, verbose_name="Date de commande", null=True, blank=True)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix total", null=True, blank=True)
    paye = models.BooleanField(default=False, verbose_name="Payée")

    def __str__(self):
        statut = "Payée" if self.paye else "Non payée"
        date_str = self.date_commande.strftime('%d/%m/%Y %H:%M') if self.date_commande else ""
        return f"Commande de {self.nom or self.utilisateur} - {date_str} - {statut}"

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_commande']


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="lignes")
    produit = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite}"


class Review(models.Model):
    product = models.ForeignKey('Product', related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.IntegerField(default=5)
    commentaire = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f"Avis de {self.user.username} - {self.note}/5"
