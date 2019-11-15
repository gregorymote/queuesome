import os
import sys
import json
import spotipy
import webbrowser
import time
import random
import util_custom as util
from json.decoder import JSONDecodeError

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from party.forms import LoginForm
from party.forms import NamePartyForm
from party.forms import CreateUserForm
from party.forms import AuthForm
from party.forms import ChooseDeviceForm
from game.forms import blankForm
from party.models import Party
from party.models import Users
from party.models import Devices

my_IP='q-it-up.herokuapp.com'
#my_IP='localhost'
my_PORT='8000'
secret=''
#uri = 'http://' + my_IP + ':' + my_PORT + '/party/auth/'
uri = 'http://' + my_IP + '/party/auth/'

scope = 'user-read-private user-read-playback-state user-modify-playback-state'
cl_id='6de276d9e60548d5b05a7af92a5db3bb'

def login(request):
    url = ''
    if request.method == 'POST':

        form = LoginForm(request.POST)
        if form.is_valid():
           
            uname = form.cleaned_data['username']
            
            unique = False

            while not unique:
                auth_code = getCode(4)
                try:
                    Party.objects.get(code=auth_code)
                except:
                    unique = True
            p = Party(name='creating party', code=auth_code, username=uname)
            p.save()
            
            try:
                url = util.generateURL(uname, scope, client_id=cl_id, client_secret=secret, redirect_uri= uri)
            except (AttributeError, JSONDecodeError):
                os.remove(f".cache-{username}")
                url = util.generateURL(username, scope, client_id=cl_id ,client_secret=secret, redirect_uri= uri)

            p.url_open = url
            p.save()
            return HttpResponseRedirect(reverse('your_code', kwargs={'pid':p.pk, 'code':auth_code}))
            
    else:
        form = LoginForm(initial= {'username' : ''})
    
    context = {
        'form' : form,
        }

    return render(request, 'party/login.html', context)

def your_code(request, pid, code):

    #if not checkPermission(pid, request):
        #return HttpResponseRedirect(reverse('start'))
        
    
    p = Party.objects.get(pk = pid)
    
    isVisible = False
    
    if p.url != None and p.token == None:
        
        try:
            p.token = util.createToken(p.url, p.username, scope, client_id=cl_id, client_secret=secret, redirect_uri= uri)
            p.save()
        except (AttributeError, JSONDecodeError):
            os.remove(f".cache-{username}")
            p.token = util.createToken(p.url, p.username, scope, client_id=cl_id ,client_secret=secret, redirect_uri= uri)
            p.save()
        isVisible = True

    if request.method == 'POST':
        form = blankForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect(reverse('choose_device', kwargs={'pid':p.pk,}))

    else:
        form = blankForm(initial ={'blank':''})

    context = {
               'form':form,
               'code':code,
               'isVisible': isVisible,
               'url': p.url_open,
               }
    return render(request, 'party/your_code.html', context)


def choose_device(request, pid):
    
    p = Party.objects.get(pk = pid)   
    spotifyObject = spotipy.Spotify(auth=p.token)
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

            return HttpResponseRedirect(reverse('start_party', kwargs={'pid':p.pk,}))

    else:
        form = ChooseDeviceForm( partyObject=p, initial = {'device':''})
        
    context = {'form': form,}
            
    return render(request, 'party/choose_device.html',context)



def auth(request):

    url = getURL(str(request.get_full_path))

    if request.method == 'POST':

        form = AuthForm(request.POST)

        if form.is_valid():
            auth_code = form.cleaned_data['auth_code']
            try:
                p = Party.objects.get(code=auth_code)
                p.url = url
                p.url_open = ''
                p.save()
                return HttpResponseRedirect(reverse('complete'))
            except:
                print("could not find party with auth code: " + auth_code)
    else:
        form = AuthForm(initial={'auth_code':''})
    
    context = {'form': form,}
    
    return render(request, 'party/auth.html', context)


def complete(request):

    return render(request, 'party/complete.html')

def name_party(request, pid):

    p = Party.objects.get(pk = pid)

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
            
            u = Users(
                name = form.cleaned_data['user_name'],
                party = p,
                sessionID = request.session.session_key,
                points = 0,
                isHost = True,
                hasSkip = True,
                hasPicked = False,
                turn = "not_picked",
                )
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
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            try:
                p = Party.objects.get(joinCode=form.cleaned_data['party_code'].upper())
                q = Users.objects.filter(party=p, sessionID=request.session.session_key)
                if q:
                    return HttpResponseRedirect(reverse('lobby', kwargs={'pid':p.pk}))
                u = Users(
                        name= form.cleaned_data['user_name'],
                        party = p,
                        sessionID = request.session.session_key,
                        points = 0,
                        isHost = False,
                        hasSkip = True,
                        hasPicked = False,
                        turn = "not_picked",
                        )
                u.save()

                return HttpResponseRedirect(reverse('lobby', kwargs={'pid':p.pk}))

            except:
                invalid = True
    else:
        form = CreateUserForm(initial={
                                        'party_choice': '',
                                        'user_name': ''})

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

    i = 0
    while path[i] != '/':
        i = i + 1
    start = i

    while path[i] != '\'':
        i = i + 1
    end = i

    url = my_IP + ':' + my_PORT + path[start:end]

    return url

def getUser(request, p):
    
    sk = request.session.session_key
    current_user = Users.objects.filter(sessionID = sk, party = p)
    current_user = list(current_user)
    u = current_user[0]
    return u

def checkPermission(pid, request):
    
    p = Party.objects.get(pk = pid)
    u = getUser(request, p)

    queury = Users.objects.filter(party = p, pk=u.pk)

    if queury:
        return True
    else:
        return False
                                         
                                           
