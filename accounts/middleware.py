import datetime
from django.utils.timezone import now

class ActiveUserMiddleware:
    """
    Middleware pour mettre à jour le dernier accès utilisateur,
    afin de détecter s'il est en ligne (champ CustomUser.last_activity).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            now_time = now()
            request.session['last_activity'] = now_time.isoformat()

            # Mettre à jour dans la base de données uniquement si > 1 min écoulée (pour éviter trop d'écritures)
            if not request.user.last_activity or (now_time - request.user.last_activity).seconds > 60:
                request.user.last_activity = now_time
                request.user.save(update_fields=["last_activity"])

        return response
