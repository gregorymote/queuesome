import os
import json
import spotipy
import time
from utils.util_auth import create_token, check_token, get_url
from utils.util_user import get_user, check_permission
from utils.util_party import get_inactivity
from utils.util_rand import get_code
from json.decoder import JSONDecodeError
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from party.models import Party, Users, Devices
from party.forms import NamePartyForm, CreateUserForm, ChooseDeviceForm
from queue_it_up.settings import (IP, PORT, URI, SCOPE, CLIENT_ID,
    CLIENT_SECRET, HEROKU)


def auth(request):
    try:
        u = Users.objects.get(
            sessionID=request.session.session_key,
            active=True
        )
    except Exception:
        return HttpResponseRedirect(reverse('index'))
    p = u.party
    url = get_url(str(request.get_full_path), HEROKU, IP, PORT)
    if 'access_denied' in url:
        return HttpResponseRedirect(reverse('index'))
    p.url = url
    p.save()
    token_info = create_token(
        url=p.url,
        scope=SCOPE,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=URI
    )
    if token_info:
        p.token = token_info['access_token']
        p.token_info = token_info
        p.save()
    else:
        return HttpResponseRedirect(reverse('index'))
    return HttpResponseRedirect(
        reverse('choose_device', kwargs={'pid': p.pk, })
    )


def choose_device(request, pid):
    if not check_permission(pid, request):
        return HttpResponseRedirect(reverse('index'))
    p = Party.objects.get(pk=pid)
    token = check_token(
        token_info=p.token_info,
        party_id=pid,
        scope=SCOPE,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=URI
    )
    spotify_object = spotipy.Spotify(auth=token)
    device_results = spotify_object.devices()['devices']
    active_devices = []

    for device in device_results:
        active_devices.append(device['id'])
        try:
            Devices.objects.get(party=p, deviceID=device['id'])
        except Exception:
            d = Devices(name=device['name'], deviceID=device['id'], party=p)
            d.save()
    all_devices = Devices.objects.filter(party=p).all()
    for device in all_devices:
        if device.deviceID not in active_devices:
            device.delete()

    if request.method == 'POST':
        form = ChooseDeviceForm(request.POST, partyObject=p)
        if form.is_valid():
            device = form.cleaned_data['device']
            p.deviceID = device.deviceID
            p.save()
            Devices.objects.filter(party=p).all().delete()
            return HttpResponseRedirect(
                reverse('start_party', kwargs={'pid': p.pk})
            )
    else:
        form = ChooseDeviceForm(partyObject=p, initial={'device': ''})
    context = {
        'form': form,
        'party': p,
    }
    return render(request, 'party/choose_device.html', context)


def update_devices(request):
    pid = request.GET.get('pid', None)
    p = Party.objects.get(pk=pid)
    token = check_token(
        token_info=p.token_info,
        party_id=pid,
        scope=SCOPE,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=URI
    )
    spotify_object = spotipy.Spotify(auth=token)
    device_results = spotify_object.devices()['devices']
    active_devices = []
    for device in device_results:
        active_devices.append(device['id'])
    refresh = False
    devices = Devices.objects.filter(party=p)
    for device in devices:
        if device.deviceID not in active_devices:
            refresh = True
            break
    if not refresh and len(devices) != len(device_results):
        refresh = True
    stop = False
    if get_inactivity(pid,2):
        stop = True
    data = {
        'refresh': refresh,
        'stop': stop
    }
    return JsonResponse(data)


def name_party(request, pid):
    if not check_permission(pid, request):
        return HttpResponseRedirect(reverse('index'))
    p = Party.objects.get(pk=pid)
    u = get_user(request, p)
    if p.started:
        return HttpResponseRedirect(reverse('lobby', kwargs={'pid': p.pk}))
    if request.method == 'POST':
        form = NamePartyForm(request.POST)
        if form.is_valid():
            p.name = form.cleaned_data['party_name']
            unique = False
            while not unique:
                join_code = get_code(4)
                try:
                    Party.objects.get(joinCode=join_code)
                except Exception:
                    p.joinCode = join_code
                    unique = True
            p.save()
            u.name = form.cleaned_data['user_name']
            u.save()
            return HttpResponseRedirect(reverse('lobby', kwargs={'pid': p.pk}))
    else:
        form = NamePartyForm(
            initial={
                'party_name': '',
                'user_name': ''
            }
        )
    context = {
        'form': form,
    }
    return render(request, 'party/name_party.html', context)


def join_party(request):
    invalid = False
    session_key = request.session.session_key
    if not session_key:
        session_key = request.session.create()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            p = Party.objects.filter(
                joinCode=form.cleaned_data['party_code'].upper(), active=True
            ).first()
            if p:  
                name = form.cleaned_data['user_name']
                user = Users.objects.filter(
                    party=p, sessionID=session_key, active=True).first()
                if user:
                    user.name = name
                    user.turn = 'not_picked'
                else:
                    u = Users(
                        name=name,
                        party=p,
                        sessionID=session_key,
                    )
                u.save()
                return HttpResponseRedirect(
                    reverse('lobby', kwargs={'pid': p.pk})
                )
            else:
                invalid = True
    else:
        code = request.GET.get('code', '')[:4]
        form = CreateUserForm(
            initial={
                'party_code': code,
                'user_name': ''
            }
        )
    context = {
        'form': form,
        'invalid': invalid,
    }
    return render(request, 'party/join_party.html', context)
