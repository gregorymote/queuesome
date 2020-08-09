from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from party.models import Party, Users
from queue_it_up.settings import CLIENT_ID, CLIENT_SECRET, SCOPE, URI
from game.forms import blankForm
import util_custom as util


def start(request):
    if not request.session.session_key:
        sk = request.session.create()
    else:
        sk = request.session.session_key
    url = ''
    if request.method == 'POST':

        form = blankForm(request.POST)
        if form.is_valid():
            uname = 'temp'
            
            p = Party(name='creating party')
            p.save()
            old_users = Users.objects.filter(sessionID=sk, active=True)
            for u in old_users:
                old_party = u.party
                old_party.active=False
                old_party.save()
                u.active = False
                u.save()
            
            u = Users(
                name = 'Host',
                party = p,
                sessionID = sk,
                points = 0,
                isHost = True,
                hasSkip = True,
                hasPicked = False,
                turn = "not_picked",
                )
            u.save()
            print("******************")
            print("**** "+URI+" ******")
            print("******************")
            try:
                url = util.generateURL(uname, SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=URI)
            except (AttributeError, JSONDecodeError):
                os.remove(f".cache-{username}")
                url = util.generateURL(uname, SCOPE, client_id=CLIENT_ID ,client_secret=CLIENT_SECRET, redirect_uri=URI)

            p.url_open = url
            p.save()
            print("******************")
            print("**** "+url+" ******")
            print("******************")
            return HttpResponseRedirect(url)
            
    else:
        form = blankForm(initial= {'blank' : ''})
    
    context = {
        'form' : form,
        }

    return render(request, 'start.html', context)


def index(request):
    if not request.session.session_key:
        sk = request.session.create()
    else:
        sk = request.session.session_key
    url = ''
    if request.method == 'POST':

        form = blankForm(request.POST)
        if form.is_valid():
            uname = 'temp'
            
            p = Party(name='creating party')
            p.save()
            old_users = Users.objects.filter(sessionID=sk, active=True)
            for u in old_users:
                old_party = u.party
                old_party.active=False
                old_party.save()
                u.active = False
                u.save()
            
            u = Users(
                name = 'Host',
                party = p,
                sessionID = sk,
                points = 0,
                isHost = True,
                hasSkip = True,
                hasPicked = False,
                turn = "not_picked",
                )
            u.save()
            
            try:
                url = util.generateURL(uname, SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=URI)
            except (AttributeError, JSONDecodeError):
                os.remove(f".cache-{username}")
                url = util.generateURL(uname, SCOPE, client_id=CLIENT_ID ,client_secret=CLIENT_SECRET, redirect_uri=URI)

            p.url_open = url
            p.save()
            return HttpResponseRedirect(url)
            
    else:
        form = blankForm(initial= {'blank' : ''})
    
    context = {
        'form' : form,
        }

    return render(request, 'index.html', context)


def start_archive(request):
    if not request.session.session_key:
        request.session.create()
 
       
    return render(request, 'start.html', {})

def index_archive(request):
    if not request.session.session_key:
        request.session.create()
    sk = request.session.session_key
       
    return render(request, 'index.html', {})

def sandbox(request):
    if not request.session.session_key:
        sk = request.session.create()
    else:
        sk = request.session.session_key
    url = ''
    if request.method == 'POST':

        form = blankForm(request.POST)
        if form.is_valid():
            uname = 'temp'
            
            p = Party(name='creating party')
            p.save()
            old_users = Users.objects.filter(sessionID=sk, active=True)
            for u in old_users:
                old_party = u.party
                old_party.active=False
                old_party.save()
                u.active = False
                u.save()
            
            u = Users(
                name = 'Host',
                party = p,
                sessionID = sk,
                points = 0,
                isHost = True,
                hasSkip = True,
                hasPicked = False,
                turn = "not_picked",
                )
            u.save()
            
            try:
                url = util.generateURL(uname, SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=URI)
            except (AttributeError, JSONDecodeError):
                os.remove(f".cache-{username}")
                url = util.generateURL(uname, SCOPE, client_id=CLIENT_ID ,client_secret=CLIENT_SECRET, redirect_uri=URI)

            p.url_open = url
            p.save()
            return HttpResponseRedirect(url)
            
    else:
        form = blankForm(initial= {'blank' : ''})
    
    context = {
        'form' : form,
        }

    return render(request, 'sandbox.html', context)

