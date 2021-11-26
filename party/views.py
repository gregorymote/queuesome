import spotipy
from utils.util_auth import create_token, check_token, get_url
from utils.util_user import get_user, check_permission
from utils.util_party import get_inactivity
from utils.util_rand import get_code
from utils.util_device import get_devices, get_active_device
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from party.models import Party, Users, Devices
from party.forms import (NamePartyForm, CreateUserForm, ChooseDeviceForm,
 BlankForm)
from queue_it_up.settings import IP, PORT, HEROKU, QDEBUG


def auth(request):
    try:
        user = Users.objects.get(
            sessionID=request.session.session_key,
            active=True
        )
    except Exception:
        return HttpResponseRedirect(reverse('index'))
    party = user.party
    url = get_url(str(request.get_full_path), HEROKU, IP, PORT)
    if 'access_denied' in url:
        return HttpResponseRedirect(reverse('index'))
    party.url = url
    party.save()
    token_info = create_token(url=party.url)
    if token_info:
        party.token = token_info['access_token']
        party.token_info = token_info
        party.save()
    else:
        return HttpResponseRedirect(reverse('index'))
    return HttpResponseRedirect(
        reverse('set_device', kwargs={'pid': party.pk,})
    )


def set_device(request, pid):
    if not check_permission(pid, request):
        return HttpResponseRedirect(reverse('index'))
    party = Party.objects.get(pk=pid)
    party.save()
    device = get_active_device(party)
    if request.method == 'POST':
        form = BlankForm(request.POST)
        if form.is_valid():
            party.deviceID = device['id']
            party.save()
            return HttpResponseRedirect(
                reverse('start_party', kwargs={'pid': party.pk})
            )
    else:
        form = BlankForm(initial={'device': ''})
    context = {
        'form': form,
        'device':device,
        'party':party
    }
    return render(request, 'party/set_device.html', context)


def update_set_device(request):
    pid = request.GET.get('pid', None)
    party = Party.objects.get(pk=pid)
    device = get_active_device(party)
    if device["id"] != party.deviceID and device["id"]:
        party.deviceID = device['id']
        party.device_error = False
        party.save()
        print(QDEBUG,'Set Party Device')
    if get_inactivity(pid,20):
        stop = True
    else:
        stop = False
    data = {
        'device': device,
        'stop': stop
    }
    return JsonResponse(data)

#OBE
def choose_device(request, pid):
    if not check_permission(pid, request):
        return HttpResponseRedirect(reverse('index'))
    party = Party.objects.get(pk=pid)
    get_devices(party)
    if request.method == 'POST':
        form = ChooseDeviceForm(request.POST, partyObject=party)
        if form.is_valid():
            device = form.cleaned_data['device']
            party.deviceID = device.deviceID
            party.save()
            Devices.objects.filter(party=party).all().delete()
            return HttpResponseRedirect(
                reverse('start_party', kwargs={'pid': party.pk})
            )
    else:
        form = ChooseDeviceForm(partyObject=party, initial={'device': ''})
    context = {
        'form': form,
        'party': party,
    }
    return render(request, 'party/choose_device.html', context)

#OBE
def update_devices(request):
    pid = request.GET.get('pid', None)
    party = Party.objects.get(pk=pid)
    token = check_token(token_info=party.token_info, party_id=pid)
    spotify_object = spotipy.Spotify(auth=token)
    device_results = spotify_object.devices()['devices']
    active_devices = []
    for device in device_results:
        active_devices.append(device['id'])
    refresh = False
    devices = Devices.objects.filter(party=party)
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
    party = Party.objects.get(pk=pid)
    device = get_active_device(party)
    user = get_user(request, party)
    if user == -1:
        return HttpResponseRedirect(reverse('index'))
    if party.name or party.started:
        return HttpResponseRedirect(reverse('lobby', kwargs={'pid': party.pk}))
    if request.method == 'POST':
        form = NamePartyForm(request.POST)
        if form.is_valid():
            party.name = form.cleaned_data['party_name']
            unique = False
            while not unique:
                join_code = get_code(4)
                try:
                    Party.objects.get(joinCode=join_code)
                except Exception:
                    party.joinCode = join_code
                    unique = True
            party.save()
            user.name = form.cleaned_data['user_name']
            user.save()
            return HttpResponseRedirect(
                reverse('lobby', kwargs={'pid': party.pk})
            )
    else:
        form = NamePartyForm(
            initial={
                'party_name': '',
                'user_name': ''
            }
        )
    context = {
        'form': form,
        'device': device,
        'party': party
    }
    return render(request, 'party/name_party.html', context)


def join_party(request):
    invalid = False
    session_key = request.session.session_key
    party_name = ""
    host = ""
    if not session_key:
        session_key = request.session.create()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['party_code'].upper() 
            party = Party.objects.filter(joinCode=code, active=True).first()
            if party:  
                name = form.cleaned_data['user_name']
                user = Users.objects.filter(
                    party=party, sessionID=session_key, active=True).first()
                if user:
                    user.name = name
                    user.turn = 'not_picked'
                else:
                    user = Users(
                        name=name,
                        party=party,
                        sessionID=session_key,
                    )
                user.save()
                return HttpResponseRedirect(
                    reverse('lobby', kwargs={'pid': party.pk})
                )
            else:
                invalid = True
    else:
        code = request.GET.get('code', '')[:4]
        party = Party.objects.filter(
                joinCode=code.upper(), active=True
            ).first()
        if party:
            party_name = party.name
            host = Users.objects.filter(party=party, isHost=True).first()
            host = host.name

        form = CreateUserForm(
            initial={
                'party_code': code,
                'user_name': ''
            }
        )
    context = {
        'form': form,
        'invalid': invalid,
        'party_name': party_name,
        'host': host
    }
    return render(request, 'party/join_party.html', context)
