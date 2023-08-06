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
    if request.method == 'POST':
        form = blankForm(request.POST)
        if form.is_valid():
            url = generate_url(
                scope=SCOPE,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=URI
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