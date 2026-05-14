import json
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import Product, Commande, Review, LigneCommande, Discussion, Message, Category
from accounts.forms import ProductForm

def index(request):
    item_name = request.GET.get("item_name")
    category = request.GET.get("category")
    product_object = Product.objects.all().order_by("-date_ajouter")
    if item_name:
        product_object = product_object.filter(nom__icontains=item_name)
    if category and category != 'Toutes':
        product_object = product_object.filter(category__nom=category)
    paginator = Paginator(product_object, 8)
    page = request.GET.get("page")
    product_object = paginator.get_page(page)
    return render(request, "shop/index.html", {"product_object": product_object})

@login_required
def detail(request, myid):
    product = get_object_or_404(Product, id=myid)
    reviews = Review.objects.filter(product=product).order_by("-date_added")
    existing_review = Review.objects.filter(product=product, user=request.user).first()
    if request.method == 'POST':
        note = int(request.POST.get('note', 5))
        commentaire = request.POST.get('commentaire', '').strip()
        if commentaire:
            if existing_review:
                existing_review.note = note
                existing_review.commentaire = commentaire
                existing_review.save()
            else:
                Review.objects.create(product=product, user=request.user, note=note, commentaire=commentaire)
            return redirect('detail', myid=product.id)
    return render(request, "shop/detail.html", {"product": product, "reviews": reviews, "existing_review": existing_review})

def paiement(request):
    if request.method == "POST":
        panier_json = request.POST.get("panier")
        nom = request.POST.get("nom")
        email = request.POST.get("email")
        adresse = request.POST.get("address")
        ville = request.POST.get("ville")
        pays = request.POST.get("pays")
        code_postal = request.POST.get("zipcode")
        
        try:
            panier_dict = json.loads(panier_json) if panier_json else {}
        except Exception:
            panier_dict = {}
        
        # Convertir le panier en liste avec calcul du total
        prix_total = 0
        panier_items = []
        
        if isinstance(panier_dict, dict):
            for pid, item in panier_dict.items():
                quantite = item.get('quantite', 1)
                prix_unitaire = float(item.get('prix_unitaire', 0))
                prix_total += quantite * prix_unitaire
                panier_items.append({
                    'produit_id': int(pid),
                    'quantite': quantite,
                    'prix_unitaire': prix_unitaire
                })
        
        # Créer la commande
        commande = Commande.objects.create(
            utilisateur=request.user if request.user.is_authenticated else None,
            nom=nom, email=email, adresse=adresse, ville=ville, pays=pays,
            code_postal=code_postal, prix_total=prix_total, paye=False,
        )
        
        # Créer les lignes de commande
        for item in panier_items:
            try:
                produit = Product.objects.get(id=item['produit_id'])
                LigneCommande.objects.create(
                    commande=commande, produit=produit,
                    quantite=item['quantite'], prix_unitaire=item['prix_unitaire']
                )
            except Product.DoesNotExist:
                pass
        
        # Vider le panier de la session et envoyer l'email
        request.session['panier'] = {}
        request.session.modified = True
        send_confirmation_email(nom, email, prix_total, commande.id)
        
        return render(request, "shop/confirmation.html", {
            "nom": nom, "email": email, "prix_total": prix_total,
            "payer": False, "commande_id": commande.id
        })
    return render(request, "shop/panier.html")

def confirmation(request):
    # Récupérer le dernier message de confirmation
    return render(request, "shop/confirmation.html")

def send_confirmation_email(nom, email, prix_total, commande_id):
    sujet = f"Confirmation commande n°{commande_id}"
    message = f"Bonjour {nom},\nVotre commande de {prix_total} FCFA est confirmée.\nMerci pour votre confiance."
    send_mail(sujet, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

@require_http_methods(["POST"])
def ajouter_panier_api(request):
    product_id = request.POST.get('product_id')
    try:
        produit = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Produit introuvable'}, status=404)
    panier = request.session.get('panier', {})
    pid = str(product_id)
    if pid in panier:
        panier[pid]['quantite'] += 1
    else:
        panier[pid] = {'quantite': 1, 'nom': produit.nom, 'prix_unitaire': float(produit.prix)}
    request.session['panier'] = panier
    return JsonResponse({'success': True})

@require_http_methods(["POST"])
def retirer_panier_api(request):
    product_id = request.POST.get('product_id')
    panier = request.session.get('panier', {})
    pid = str(product_id)
    if pid in panier:
        if panier[pid]['quantite'] > 1:
            panier[pid]['quantite'] -= 1
        else:
            del panier[pid]
        request.session['panier'] = panier
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Non présent'}, status=400)

def get_panier_info(request):
    panier = request.session.get('panier', {})
    total = 0
    quantite_totale = 0
    for item in panier.values():
        q = item['quantite']
        prix = item['prix_unitaire']
        total += q * prix
        quantite_totale += q
    return JsonResponse({'panier': panier, 'total': total, 'quantite_totale': quantite_totale})

@login_required
def ajouter_produit(request):
    if request.method == 'POST':
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

@login_required
def modifier_produit(request, pk):
    produit = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('mes_produits')
    else:
        form = ProductForm(instance=produit)
    return render(request, 'shop/modifier_produit.html', {'form': form, 'produit': produit})

@login_required
def supprimer_produit(request, pk):
    produit = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        produit.delete()
        return redirect('mes_produits')
    return render(request, 'shop/confirmer_suppression.html', {'produit': produit})

@login_required
@login_required
def discussion(request, vendeur_id, produit_id=None):
    """Page de discussion avec un vendeur"""
    from accounts.models import CustomUser
    vendeur = get_object_or_404(CustomUser, id=vendeur_id)
    produit = None
    if produit_id:
        produit = get_object_or_404(Product, id=produit_id)
    
    # Créer ou récupérer la discussion
    discussion_obj, created = Discussion.objects.get_or_create(
        acheteur=request.user,
        vendeur=vendeur,
        produit=produit
    )
    
    if request.method == 'POST':
        contenu = request.POST.get('contenu', '').strip()
        if contenu:
            Message.objects.create(
                discussion=discussion_obj,
                sender=request.user,
                contenu=contenu
            )
            discussion_obj.save()  # Mise à jour du date_update
            messages.success(request, 'Message envoyé avec succès!')
        
        # Rediriger vers la bonne route
        if produit_id:
            return redirect('discussion_produit', vendeur_id=vendeur_id, produit_id=produit_id)
        else:
            return redirect('discussion', vendeur_id=vendeur_id)
    
    messages_list = discussion_obj.messages.all()
    return render(request, 'shop/discussion.html', {
        'discussion': discussion_obj,
        'messages': messages_list,
        'vendeur': vendeur,
        'produit': produit
    })

def toutes_categories(request):
    """Afficher toutes les catégories et permettre d'en ajouter une nouvelle"""
    categories = Category.objects.all().order_by('-date_ajouter')
    paginator = Paginator(categories, 12)
    page = request.GET.get('page')
    categories = paginator.get_page(page)
    return render(request, 'shop/toutes_categories.html', {
        'categories': categories
    })

@login_required
def ajouter_categorie(request):
    """Ajouter une nouvelle catégorie"""
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        if nom and len(nom) >= 2:
            # Vérifier si la catégorie existe déjà
            if not Category.objects.filter(nom__iexact=nom).exists():
                Category.objects.create(nom=nom)
                messages.success(request, f'Catégorie "{nom}" ajoutée avec succès!')
                return redirect('toutes_categories')
            else:
                messages.warning(request, f'La catégorie "{nom}" existe déjà.')
        else:
            messages.error(request, 'Le nom de la catégorie doit contenir au moins 2 caractères.')
    return render(request, 'shop/ajouter_categorie.html')