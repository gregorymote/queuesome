from party.models import Party, Users
from datetime import datetime, timedelta, timezone
from utils.util_user import get_user
from queue_it_up.settings import SYSTEM

def check_active(pid, request):
    try:
        p = Party.objects.get(pk = pid)
        users = Users.objects.filter(party=p, active=True)
        if not p.active:
            return False
        elif not users :
            return False
        else:
            u = get_user(request, p)
            if u.name != SYSTEM:
                return u.active
            else:
                return True
    except Exception:
        return False

def get_inactivity(pid, duration):
    p = Party.objects.get(pk=pid)
    now = datetime.now(timezone.utc)
    inactivity = ((now - p.last_updated).seconds // 60) % 60
    return inactivity > duration


def clean_up_party(pid):
    p = Party.objects.get(pk=pid)
    p.active=False
    p.token = ""
    p.token_info = ""
    p.url = ""
    p.url_open = ""
    p.deviceID = ""
    p.save()