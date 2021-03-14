from django.http import HttpResponseRedirect
from django.urls import reverse
from party.models import Party, Users, Songs

def get_user(request, party):
    session_key = request.session.session_key
    try:
        current_user = Users.objects.get(
            sessionID=session_key, party=party, active=True
        )
    except Exception:
        return HttpResponseRedirect(reverse('index'))

    return current_user


def check_permission(pid, request):
    try:
        p = Party.objects.get(pk=pid, active=True)
    except Exception:
        return False
    session_key = request.session.session_key
    try:
        u = Users.objects.get(sessionID=session_key, party = p)
    except Exception:
        return False
    if not u.isHost:
        return False
    else:
        return True


def like_song(song, user, request):
    if song and not song.duplicate:
        if 'like' in request.POST:
            song.likes += 1
        else:
            song.likes -= 1
        song.save()
        user.hasLiked = True
        user.save()
