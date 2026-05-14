from .models import Category

def categories_processor(request):
    # Limiter à 8 catégories pour la navbar
    categories_nav = Category.objects.all()[:8]
    # Vérifier s'il y a plus de catégories
    has_more_categories = Category.objects.count() > 8
    return {
        'categories_nav': categories_nav,
        'has_more_categories': has_more_categories,
        'total_categories': Category.objects.count()
    }