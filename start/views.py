from django.shortcuts import render
from utils.util_auth import generate_url
from django.http import HttpResponseRedirect
from party.models import Party, Users
from game.forms import blankForm
from queue_it_up.settings import (CLIENT_ID, CLIENT_SECRET, SCOPE, URI, HEROKU,
    STAGE)


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
            party = Party()
            party.save()
            old_users = Users.objects.filter(sessionID=session_key, active=True)
            for user in old_users:
                if user.isHost:
                    old_party=user.party
                    old_party.active=False
                    old_party.save()
                user.active = False
                user.save()
            user = Users(
                    name='Host',
                    party=party,
                    sessionID=session_key,
                    isHost=True,
            )
            user.save()
            url = generate_url(
                scope=SCOPE,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=URI
            )
            party.url_open=url
            party.save()
            return HttpResponseRedirect(url)
    else:
        form = blankForm(initial= {'blank' : ''})
    context = {
        'form' : form,
    }
    return render(request, 'index.html', context)


def about(request):       
    return render(request, 'about.html', {})