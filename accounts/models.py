from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

    @property
    def is_online(self):
        """Retourne True si l'utilisateur est actif dans les 5 dernières minutes."""
        if not self.last_activity:
            return False
        return timezone.now() - self.last_activity <= timedelta(minutes=5)

    @property
    def is_admin(self):
        """Retourne True si l'utilisateur est un administrateur."""
        return self.is_staff or self.is_superuser

    @property
    def is_admin_online(self):
        """Retourne True si l'utilisateur est admin ET en ligne."""
        return self.is_admin and self.is_online
