from .models import Category

def categories_processor(request):
    return {'categories_nav': Category.objects.all()}