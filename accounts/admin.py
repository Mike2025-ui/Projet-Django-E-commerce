from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.html import format_html

# ✅ Personnalisation de l'affichage admin
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'photo_tag', 'is_staff', 'is_active')
    readonly_fields = ('photo_tag',)

    def photo_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.photo.url)
        return "-"
    photo_tag.short_description = 'Photo'

admin.site.register(CustomUser, CustomUserAdmin)