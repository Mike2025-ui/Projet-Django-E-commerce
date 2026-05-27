from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    photo = models.ImageField(upload_to="photos/", blank=True, null=True)

    def __str__(self):
        return self.username

    @property
    def photo_url(self):
        """Retourne l'URL de la photo ou l'avatar par défaut"""
        if self.photo:
            return self.photo.url
        return "/default-avatar/"

    @property
    def is_admin(self):
        return self.is_staff or self.is_superuser
