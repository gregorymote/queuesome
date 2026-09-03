import secrets

from django.shortcuts import render
from django.http import HttpResponseRedirect

from game.forms import blankForm
from queue_it_up.settings import (CLIENT_ID, CLIENT_SECRET, SCOPE, URI, HEROKU,
    STAGE)
from utils.util_auth import OAUTH_STATE_SESSION_KEY, generate_url


def start(request):  
    form = blankForm(initial= {'blank' : ''})
    context = {
        'form' : form,
        'HEROKU': HEROKU,
        'STAGE': STAGE
    }
    return render(request, 'start.html', context)


def index(request):
    if request.method == 'POST':
        form = blankForm(request.POST)
        if form.is_valid():
            state = secrets.token_urlsafe(32)
            request.session[OAUTH_STATE_SESSION_KEY] = state
            url = generate_url(
                scope=SCOPE,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=URI,
                state=state,
            )
            return HttpResponseRedirect(url)
    else:
        form = blankForm(initial= {'blank' : ''})
    context = {
        'form' : form,
    }
    return render(request, 'index.html', context)


def about(request):       
    return render(request, 'tutorial.html', {})


def tutorial(request):
    return render(request, 'tutorial.html', {})
