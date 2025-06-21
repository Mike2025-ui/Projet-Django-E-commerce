from datetime import timedelta
from django.utils.timezone import now

def is_user_online(last_activity_iso, timeout_seconds=300):
    """
    Retourne True si la dernière activité est récente (ex: 5 minutes).
    """
    if not last_activity_iso:
        return False
    last_activity = now().fromisoformat(last_activity_iso)
    delta = now() - last_activity
    return delta.total_seconds() < timeout_seconds
