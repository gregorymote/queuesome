from party.models import Party, Users, Library
from datetime import datetime, timedelta, timezone
from queue_it_up.settings import SYSTEM
from django.http import HttpResponseRedirect

def get_party(pid):
    try:
        return Party.objects.get(pk=pid)
    except Exception:
        return HttpResponseRedirect(reverse('index'))


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


def set_lib_repo():
    lib_set = set()
    libraries = Library.objects.filter(visible=True).exclude(special=True)
    for library in libraries:
        lib_set.add(library.id)
    return lib_set