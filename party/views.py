import os
import sys
import json
import spotipy
import webbrowser
import time
import random
import util_custom as util
from json.decoder import JSONDecodeError
from ast import literal_eval
from spotipy import oauth2

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from party.forms import LoginForm, NamePartyForm, CreateUserForm, AuthForm, ChooseDeviceForm
from game.forms import blankForm
from party.models import Party, Users, Devices
from queue_it_up.settings import IP, PORT, URI, SCOPE, CLIENT_ID, CLIENT_SECRET 


def login(request):
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

    return render(request, 'party/login.html', context)


def choose_device(request, pid):
    if not checkPermission(pid, request):
        return HttpResponseRedirect(reverse('index'))
                                     
    p = Party.objects.get(pk = pid)
    token = checkToken(p.token_info, pid)
    if token is None:
        token = p.token
    spotifyObject = spotipy.Spotify(auth=token)
    deviceResults = spotifyObject.devices()
    deviceResults = deviceResults['devices']
    curr_devices = []

    for x in deviceResults:
        curr_devices.append(x['id'])
                            
    for x in deviceResults:
        try:
            Devices.objects.get(party=p, deviceID= x['id'])
        except:
            d = Devices(name = x['name'], deviceID = x['id'], party = p)
            d.save()
    query = Devices.objects.filter(party=p)
    for x in query:
        if x.deviceID  not in curr_devices:
            x.delete()

    if request.method == 'POST':
        form = ChooseDeviceForm(request.POST, partyObject=p)

        if form.is_valid():

            device = form.cleaned_data['device']
            p.deviceID=device.deviceID
            p.save()
            Devices.objects.filter(party=p).all().delete()
            return HttpResponseRedirect(reverse('start_party', kwargs={'pid':p.pk,}))

    else:
        form = ChooseDeviceForm( partyObject=p, initial = {'device':''})
        
    context = {'form': form,}
            
    return render(request, 'party/choose_device.html',context)


def auth(request):
    try:
        u = Users.objects.filter(sessionID=request.session.session_key, active=True).first()
    except:
         return HttpResponseRedirect(reverse('index'))
    p = u.party
    url = getURL(str(request.get_full_path))
    p.url = url
    p.save()
    
    try:
        token_info = util.createToken(p.url, 'temp', SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri= URI)
        p.token = token_info['access_token']
        p.token_info = token_info
        p.save()
    except (AttributeError, JSONDecodeError):
        os.remove(f".cache-temp")
        token_info = util.createToken(p.url, 'temp', SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri= URI, show_dialog=False)
        p.token = token_info['access_token']
        p.token_info = token_info
        p.save()
   
    return HttpResponseRedirect(reverse('choose_device', kwargs={'pid':p.pk,}))


def name_party(request, pid):

    if not checkPermission(pid, request):
        return HttpResponseRedirect(reverse('index'))
    
    p = Party.objects.get(pk = pid)
    u = getUser(request, p)

    if p.started:
        return HttpResponseRedirect(reverse('lobby', kwargs={'pid':p.pk}))

    if request.method == 'POST':

        form = NamePartyForm(request.POST)

        if form.is_valid():
            p.name=form.cleaned_data['party_name']
            p.roundNum = 1
            p.roundTotal = 0
            p.started = False
            p.state = 'assign'

            unique = False

            while not unique:
                jc = getCode(4)
                try:
                    Party.objects.get(joinCode=jc)
                except:
                    p.joinCode = jc
                    unique = True
                   
            p.save()
            u.name = form.cleaned_data['user_name']
            u.save()
                
            return HttpResponseRedirect(reverse('lobby', kwargs={'pid':p.pk}))
        
    else:

            
        form = NamePartyForm(initial={
                                    'party_name' : '',
                                    'user_name' : ''})


    context = {
        'form' : form,
        }

    return render(request, 'party/name_party.html', context)

def create_user(request):
    invalid = False
    sk = request.session.session_key
    if not sk:
        sk = request.session.create()
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            p = Party.objects.filter(joinCode=form.cleaned_data['party_code'].upper()).first()
            if p:
                if not p.active:
                    invalid = True
                else:
                    username = form.cleaned_data['user_name']
                    q = Users.objects.filter(party=p, sessionID=sk, active=True).first()
                    if q:
                        q.active=True
                        q.name= username
                        q.turn='not_picked'
                        q.save()
                        return HttpResponseRedirect(reverse('lobby', kwargs={'pid':p.pk}))
                    u = Users(
                            name= username,
                            party = p,
                            sessionID = sk,
                            points = 0,
                            isHost = False,
                            hasSkip = True,
                            hasPicked = False,
                            turn = "not_picked",
                    )
                    u.save()

                    return HttpResponseRedirect(reverse('lobby', kwargs={'pid':p.pk}))
            else:
                invalid = True
    else:
        form = CreateUserForm(initial={
                                        'party_choice': '',
                                        'user_name': ''
                                    }
        )

    context = {
        'form' : form,
        'invalid' : invalid,
        }

    return render(request, 'party/create_user.html', context)

def getCode(i):
    code = ""                                    
    for x in range(i):
        rand = random.randint(48,122)
        while not isValid(rand):
            rand = random.randint(48,122)
        code = chr(rand) + code
    return code


def isValid(num):
    if (num >=58 and num < 65) or (num >=91) or (num == 48) or (num == 79):
        return False
    else:
        return True
    

def getURL(path):
    print('path:', path)
    i = 0
    while path[i] != '/':
        i = i + 1
    start = i

    while path[i] != '\'':
        i = i + 1
    end = i

    url = IP + ':' + PORT + path[start:end]

    return url


def getUser(request, p):
    
    sk = request.session.session_key
    try:
        current_user = Users.objects.get(sessionID = sk, party = p, active=True)
    except:
        return HttpResponseRedirect(reverse('index'))
    u = current_user
    return u

def checkPermission(pid, request):
    
    p = Party.objects.get(pk = pid)
    u = getUser(request, p)

    query = Users.objects.filter(party = p, pk=u.pk, active=True)

    if query:
        return True
    else:
        return False

def checkToken(token_info, pid):

    token_info = literal_eval(token_info)
    #print('Expires in: ', token_info['expires_at'] - time.time())
    p = Party.objects.get(pk = pid)
    
    cache_path = ".cache-" + 'temp'

    sp_oauth = oauth2.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, URI, 
        scope=SCOPE, cache_path=cache_path)
    
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        #print('token_info:', token_info)
        p.token = token_info['access_token'] ##
        p.token_info = token_info
        p.save()
        #print("TOKEN REFRESHED")
        return p.token
    else:
        #print("TOKEN STILL VALID")
        return None


def checkPermission(pid, request):
    try:
        p = Party.objects.get(pk=pid, active=True)
    except:
        return False

    sk = request.session.session_key
    try:
        u = Users.objects.get(sessionID = sk, party = p)
    except:
        return False

    if not u.isHost:
        return False
    else:
        return True
        
    
                              
                                           
