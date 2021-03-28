from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Q
from party.models import (Party, Users, Category, Library, Songs,
    Searches, Devices)
from utils.util_auth import check_token
from utils.util_user import (get_user, check_permission, like_song,
    assign_leader, reset_users)
from utils.util_party import (get_party, clean_up_party, get_inactivity,
    set_lib_repo, get_results, get_category_choices, create_category)
from utils.util_rand import get_letter, get_numbers
from utils.util_device import is_device_active, activate_device
from game.forms import (blankForm, chooseCategoryForm, searchForm,
    searchResultsForm, settingsForm)
from queue_it_up.settings import (DRIVER, DRIVER_URI, SYSTEM, HEROKU, STAGE,
    URL, IP, URI, SCOPE, CLIENT_ID, CLIENT_SECRET)
from datetime import datetime, timedelta, timezone
import spotipy
import time
import os
import threading
import webbrowser
import random


def lobby(request, pid):
    ''' Gets Users in Party and Displays them. The Party host has the ability
    to start the party by submitting the form. Submitting the form launches a
    browser window on the system and sets the party to started.

    Parameters:

        - request - web request
        - pid - Primary Key of the Party the User belongs to

    '''
    party = get_party(pid)
    if get_inactivity(pid,20):
        clean_up_party(p.pk)
    if request.method == 'POST':
        form = blankForm(request.POST)
        if form.is_valid():
            c = Category(name='Looks Like We Got A Lull', party=party)
            c.save()
            party.lib_repo = set_lib_repo()
            party.started = True
            party.save()
            if HEROKU:
                DRIVER.get(DRIVER_URI.format(str(pid)))
            else:
                print(DRIVER_URI.format(str(pid)))
                webbrowser.open(DRIVER_URI.format(str(pid)))
            return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    else:
        form = blankForm(initial={'text':'blank',})
        party = Party.objects.get(pk=pid)
        if party.started:
            return HttpResponseRedirect(reverse('play', kwargs={'pid': pid}))
    u = get_user(request, pid)
    users = Users.objects.filter(party=pid, active=True).all()
    names=[]
    for user in users:
        names.append(user.name)
    context = {
        'party':party,
        'names':names,
        'access':u.isHost,
        'form':form,
        'URL':URL,
    }
    return render(request, 'game/lobby.html', context)


def update_lobby(request):
    ''' Ajax request to update the users on the lobby page. Returns an updated
    party size, list of names, and whether the party is started or inactive. 

    Parameters:

        - request - web request

    '''
    pid = request.GET.get('pid', None)
    p = Party.objects.get(pk = pid)
    if get_inactivity(pid,20):
        clean_up_party(p.pk)
    users = Users.objects.filter(party=pid, active=True).all()
    names=[]
    for user in users:
        names.append(user.name)
    data = {
        'size': users.count(),
        'started': p.started,
        'names': names,
        'inactive': p.active
    }
    return JsonResponse(data)


def play(request, pid):
    ''' Gets the song playing and displays it with the category and party info.
    Form Post will increment/decrement the playing song's likes.

    Parameters:

        - request - web request
        - pid - Primary Key of the Party the User belongs to

    '''
    party = get_party(pid)
    if request.GET.get('user', '') == SYSTEM:
        user=Users.objects.filter(party=party, name=SYSTEM)
        if not user:
            user=Users(
                party=party,
                name=SYSTEM,
                sessionID=request.session.session_key,
                active=False,
                refreshRate=3
            )
            user.save()
    else:
        user = get_user(request, pid)

    if request.method == 'POST':
        form = blankForm(request.POST)
        if form.is_valid():
            song = Songs.objects.filter(
                state='playing', category__party=party).first()
            like_song(song, user, request)         
    else:
        form = blankForm(initial={'text':'blank',})

    song = Songs.objects.filter(category__party=party, state='playing').first()
    if song:
        category = song.category
    else:
        song = Songs(art='lull')
        category = Category.objects.filter(party=party, roundNum=0).first()
    
    results = get_results(party)
    context = {
        'form': form,
        'party': party,
        'user' : user,
        'category' : category,
        'song' : song,
        'results': results,
        'system': SYSTEM
    }
    
    return render(request, 'game/play.html', context)


def update_play(request):
    ''' Ajax request made by general user to update the play page with the
    latest info (i.e. current song and category). 
    Returns data to ensure page reflects the current play state and is showing
    latest info.  

    Parameters:

        - request - web request

    '''
    pid = request.GET.get('pid', None)
    if get_inactivity(pid,20):
        inactive = True
    else:
        inactive = False
    party = Party.objects.get(pk = pid)
    user = get_user(request, pid)

    song = Songs.objects.filter(category__party=party, state='playing').first()
    if song:
        category = song.category
    else:
        song = Songs(art='lull')
        category = Category.objects.filter(party=party, roundNum=0).first()
    
    results = get_results(party)
    party_info = {
		"device_error" : str(party.device_error),
		"name" : party.name,
		"state": party.state,
		"joinCode" : party.joinCode,
        "inactive": inactive
	}
    user_info={
	    "isHost":str(user.isHost),
		"hasPicked": str(user.hasPicked),
		"turn": user.turn,
		"hasLiked": str(user.hasLiked),
		"user": user.pk
	}
    try:
        leader = category.leader.name
    except Exception:
        leader = ""
    category_info={
		"name": category.name,
		"leader": leader,
	}
    try:
        song_user = song.user.pk
    except Exception:
        song_user = -1

    song_info= {
		"name": song.name,
		"link": song.link,
		"user": song_user,
		"art": song.art
	}
    data = {
        'party': party_info,
        'user' : user_info,
        'category' : category_info,
        'song' : song_info,
        'results':results
    }
    return JsonResponse(data)


def update_game(request):
    ''' Ajax request made by system to update the game logic 

    Parameters:

        - request - web request

    '''
    pid = request.GET.get('pid', None)   
    party = Party.objects.get(pk = pid)

    if get_inactivity(pid,20):
        clean_up_party(party.pk)
        inactive = True
    else:
        inactive = False

    if party.state == 'assign' or \
            (party.state=='choose_category' and not 
                Users.objects.filter(
                    turn='picking',
                    party=party,
                    active=True
                ).first()
            ):
        assign_leader(party)
        party.state = 'choose_category'
        party.save()  
                
    if party.state == 'pick_song' and not \
            Users.objects.filter(
                hasPicked=False,
                party=party,
                active=True
            ).all():
        reset_users(party) 
        party.state = 'assign'
        party.save()

    if not party.device_error:
        if not party.thread and \
                Songs.objects.filter(
                    category__party=party,
                    category__roundNum=party.roundNum,
                    state='not_played',
                    category__full=True
                ):
            thread = threading.Thread(target=play_songs, args=(pid,))
            thread.start()
    else:
        party.device_error = not activate_device(
            token_info=party.token_info,
            party_id=party.pk,
            scope=SCOPE,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=URI
        )
        party.save()

    song = Songs.objects.filter(category__party=party, state='playing').first()
    if song:
        category = song.category
        if party.roundNum != category.roundNum:
            party.roundNum = category.roundNum
            party.save()
    else:
        last_played = Songs.objects.filter(
            category__party=party,
            state='played'
            ).order_by('-category__roundNum').first()
        if last_played and party.roundNum != last_played.category.roundNum + 1:
            party.roundNum = last_played.category.roundNum + 1
            party.save()
    data={
        "success": 'True',
        "inactive" : inactive
        }

    return JsonResponse(data)


def choose_category(request, pid):

    party = get_party(pid)
    user = get_user(request, pid)
    if user.turn != 'picking':
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    valid=True
    choices = get_category_choices(request, party)
        
    if request.method == 'POST':
        form = chooseCategoryForm(request.POST, repo=choices)
        if form.is_valid():
            category = form.cleaned_data['cat_choice']
            valid = create_category(
                party=party,
                user=user,
                category=category,
                artist=form.cleaned_data['artist'],
                custom=form.cleaned_data['custom'],
                sc_type=form.cleaned_data['scatt_radio']
            )
            if valid:
                party.state = 'pick_song'
                party.roundTotal = party.roundTotal + 1
                party.save()
                remaining_users = Users.objects.filter(
                    party=party,
                    turn='not_picked',
                    active=True
                ).all()
                if not remaining_users:
                    user.turn = 'has_picked_last'
                else:
                    user.turn = 'has_picked'
                user.save()
                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    else:
        form = chooseCategoryForm(repo=choices,
                    initial={'cat_choice': '','custom': '',}
        )
    context = {
        'form':form,
        'party':party,
        'invalid': not valid,
    }
    return render(request, 'game/choose_category.html', context)


def pick_song(request, pid):

    party = get_party(pid)
    user = get_user(request, party)
    invalid = False
    song_list = ('')
    if user.hasPicked:
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    
    category = Category.objects.filter(
        party=party, roundNum=party.roundTotal
    ).first()

    if request.method == 'POST':
        form = searchForm(request.POST,data_list=song_list)
        if form.is_valid():
            result = form.cleaned_data['result']
            if result != '-1':
                search = Searches.objects.filter(uri=result).first()
                print(search)
                Songs(
                    name=search.name,
                    uri=search.uri,
                    art=search.art,
                    user=user,
                    category=category,
                    played=False,
                    order=random.randint(1,101),
                    state='not_played',
                    link=search.link,
                    duration=search.duration,
                ).save()
                Searches.objects.filter(user=user, party=party).delete()
                user.hasPicked = True
                user.save()
                not_picked = Users.objects.filter(
                    party=party,
                    active=True,
                    hasPicked=False
                    ).all()
                if not not_picked:
                    category.full = True
                    category.save()
                return HttpResponseRedirect(
                        reverse('play', kwargs={'pid':pid})
                )
            else:
                invalid=True
    else:
        form = searchForm(data_list=song_list)
    
    context = {
        'form':form,
        'category':category,
        'invalid':invalid,
        'party':party
    }
    return render(request, 'game/pick_song.html', context)


def update_search(request):
    ''' Ajax request made to update search results 

    Parameters:

        - request - web request

    '''
    pid = request.GET.get('pid', None)   
    party = Party.objects.get(pk = pid)
    user = get_user(request, party)
    result = request.GET.get('result', None)
    search = Searches.objects.all()

    Searches.objects.filter(user=user, party=party).exclude(uri=result).delete()
    current = Searches.objects.filter(uri=result).first()
    if current:
        print('******',current.uri,':', current.name,'**********')
    search_text = request.GET.get('text', None)
    token = check_token(
        token_info=party.token_info,
        party_id=pid,
        scope=SCOPE,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=URI
    )
    spotify_object = spotipy.Spotify(auth=token)
    search_results = spotify_object.search(search_text, 15, 0, 'track')
    tracks = search_results['tracks']['items']
    song_list = []
    for track in tracks:
        try:
            album_art = track['album']['images'][0]['url']
        except Exception:
            album_art=""
        artist_name = track['artists'][0]['name']  
        track_name = track['name']
        track_uri = track['uri']
        track_duration = track['duration_ms']
        url = track['external_urls']['spotify']
        track_name = (
            trackName[:255] + '..'
        ) if len(track_name) > 255 else track_name
        if not current or current.uri != track_uri:
            search = Searches(
                name = track_name + ", " + artist_name,
                uri=track_uri,
                art=album_art,
                party=party,
                user=user,
                link=url,
                duration=track_duration
            )
            search.save()
        else:
            search = current
        print(search.name,':',search.uri)
        song_list.append(
            {
            'track_name':search.name,
            'album_art':album_art,
            'id': search.uri,
            }
        )
    data={
        "success": 'True',
        "song_list": song_list,

    }
    return JsonResponse(data)


def settings(request, pid):

    p = get_party(pid)

    if not check_permission(pid, request):
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    
    invalid = False
    
    token = check_token(
        token_info=p.token_info,
        party_id=pid,
        scope=SCOPE,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=URI
    )
    spotify_object = spotipy.Spotify(auth=token)

    device_results = spotify_object.devices()
    device_results = device_results['devices']
    curr_devices = []

    for x in device_results:
        curr_devices.append(x['id'])
                            
    for x in device_results:
        try:
            Devices.objects.get(party=p, deviceID= x['id'])
        except Exception:
            d = Devices(name = x['name'], deviceID = x['id'], party = p)
            d.save()
    query = Devices.objects.filter(party=p)

    for x in query:
        if x.deviceID  not in curr_devices:
            x.delete()
        
    if request.method == 'POST':
        form = settingsForm(request.POST, partyObject=p)

        if form.is_valid():
            Devices.objects.filter(party=p).all().delete()
            if ('back' in request.POST):
                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))

            elif ('kill' in request.POST):
                p.active = False
                p.save()
                clean_up_party(p.pk)
                return HttpResponseRedirect(reverse('index'))
                
            else:
                device = form.cleaned_data['device']
                if device != None:
                    p.deviceID=device.deviceID
                    time = form.cleaned_data['time']
                    p.time = time
                    p.device_error = False
                    p.save()
                    return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
                else:
                    invalid = True
    else:
        form = settingsForm(partyObject=p, initial={'time':p.time,})

    context = {
                'form' : form,
                'invalid':invalid,
                }    
    return render(request, 'game/settings.html', context)


def users(request, pid):

    p = get_party(pid)
    u = get_user(request, p)
    if u.isHost:
        isHost = True
    else:
        isHost = False
    users = Users.objects.filter(party=p, active=True)

    if request.method == 'POST':
        form = blankForm(request.POST)
        if form.is_valid():
            p = Party.objects.get(pk = pid)
            if ('back' in request.POST):
                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
            elif ('skip' in request.POST):
                if p.roundNum == p.roundTotal:
                    c = Category.objects.filter(party=p, roundNum=p.roundNum).first()
                    c.full = True
                    c.save()
                    users = Users.objects.filter(party=p, active=True)
                    for x in users:
                        x.hasPicked = False
                        x.save()
                    p.state = 'assign'
                    p.save()
                elif p.roundNum > p.roundTotal:
                    lead = Users.objects.filter(party=p, turn='picking', active=True).first()
                    if lead:
                        lead.turn='picked'
                        lead.save()
                    p.state = 'assign'
                    p.save()

                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
            else:
                for x in users:
                    if (x.sessionID in request.POST):
                        x.active=False
                        x.sessionID = ""
                        x.save()
                        not_picked = Users.objects.filter(party=p, active=True, hasPicked=False)
                        if not not_picked:
                            c = Category.objects.filter(party=p, roundNum=p.roundTotal).first()
                            c.full = True
                            c.save()
                        return HttpResponseRedirect(reverse('users', kwargs={'pid':pid}))
    else:
        form = blankForm(initial={'text':'blank',})
    
    decode = {
              'True':'Yes',
              'False':'No',
              'picking':'Picking',
              'not_picked':'No',
              'has_picked':'Yes',
              'has_picked_last':'Yes',
              }
    
    context = {
                'form' : form,
                'users':users,
                'decode':decode,
                'isHost':isHost,
                
                }    
    return render(request, 'game/users.html', context)


def play_songs(pid):
    p = Party.objects.get(pk = pid)
    p.thread = True
    if not p.active:
        return
    if p.device_error:
        p.device_error = False
    p.save()
    rN = p.roundNum
    token = check_token(
        token_info=p.token_info,
        party_id=pid,
        scope=SCOPE,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=URI
    )
    spotify_object = spotipy.Spotify(auth=token)
    while (Songs.objects.filter(category__party=p, category__roundNum = rN, state='not_played', category__full=True)):
        queue = Songs.objects.filter(category__party=p, category__roundNum = rN, state='not_played', category__full=True).order_by('order')
        for song in queue:
            song = Songs.objects.get(pk=song.pk)
            ls = [song.uri]
            try:
                if not song.duplicate:
                    p = Party.objects.get(pk=pid)
                    if not p.active:
                        return
                    dups = list(Songs.objects.filter(category__party=p, category__roundNum = rN, state='not_played', name=song.name))
                    if len(dups) > 1:
                        for d in dups:
                            d.duplicate=True
                            d.save()
                            u = d.user
                            u.hasLiked=True
                            u.save()
                        song.duplicate=True
                        song.save()
                    token = check_token(
                        token_info=p.token_info,
                        party_id=pid,
                        scope=SCOPE,
                        client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=URI
                    )
                    spotify_object = spotipy.Spotify(auth=token)
                    activate_device(
                        token_info=p.token_info,
                        party_id=pid,
                        scope=SCOPE,
                        client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=URI
                    )
                    spotify_object.start_playback(device_id=p.deviceID , uris=ls)
                    song.state = 'playing'
                    song.startTime = time.time()
                    song.save()

                    num = len(list(Users.objects.filter(party = p, active=True))) * (-1) + 1
                    if num == 0:
                        num = -1
                    duration = song.duration / 1000
                    
                    if duration < p.time or song.duplicate:
                        length = duration - 5
                    else:
                        length = p.time
                    flag = True
                    while(time.time() - song.startTime < length):
                        if Songs.objects.filter(pk=song.pk, likes__lte=num):
                            break
                        if song.duplicate and (time.time() - song.startTime) >= p.time and flag:
                            song.art= "duplicate"
                            song.save()
                            flag = False
                        continue
                song = Songs.objects.filter(pk=song.pk).first()
                song.state= 'played'
                song.save()
            except Exception as e:
                p = Party.objects.get(pk = pid)
                if 'Device not found' in str(e):
                    p.device_error = True
                p.thread  = False
                p.debug = p.debug
                p.save()
                print('**************************')
                print(e)
                print('**************************')
                return
            users = Users.objects.filter(party = p, active=True)
            for x in users:
                x.hasLiked = False
                x.save()
        songs = Songs.objects.filter(category__party=p, category__roundNum = rN)
        for s in songs:
            u = s.user
            u.points = u.points + s.likes
            u.save()   
        rN = rN + 1
    p = Party.objects.get(pk = pid)
    p.thread=False
    p.save()
    print('EXITING THREAD')

