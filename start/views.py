from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from party.models import Party, Users
from queue_it_up.settings import CLIENT_ID, CLIENT_SECRET, SCOPE, URI, HEROKU, STAGE
from game.forms import blankForm
from utils.util_auth import generate_url


def start(request):  
    form = blankForm(initial= {'blank' : ''})
    context = {
        'form' : form,
        'HEROKU': HEROKU,
        'STAGE': STAGE
    }
    return render(request, 'start.html', context)


def index(request):
    if not request.session.session_key:
        session_key = request.session.create()
    else:
        session_key = request.session.session_key
    url = ''
    if request.method == 'POST':
        form = blankForm(request.POST)
        if form.is_valid():
            p = Party(name='creating party')
            p.save()
            old_users = Users.objects.filter(sessionID=session_key, active=True)
            for u in old_users:
                if u.isHost:
                    old_party = u.party
                    old_party.active=False
                    old_party.save()
                u.active = False
                u.save()
            u = Users(
                    name = 'Host',
                    party = p,
                    sessionID = session_key,
                    isHost = True,
            )
            u.save()
            url = generate_url(
                scope=SCOPE,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=URI
            )
            p.url_open = url
            p.save()
            return HttpResponseRedirect(url)
    else:
        form = blankForm(initial= {'blank' : ''})
    context = {
        'form' : form,
    }
    return render(request, 'index.html', context)


def about(request):       
    return render(request, 'about.html', {})