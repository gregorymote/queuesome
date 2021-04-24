from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Q
from party.models import (Party, Users, Category, Library, Songs,
    Searches, Devices)
from utils.util_auth import check_token
from utils.util_user import (get_user, check_permission, like_song,
    assign_leader, reset_users, set_user_points, reset_user_likes,
    get_like_threshold)
from utils.util_party import (get_party, clean_up_party, get_inactivity,
    set_lib_repo, get_results, get_category_choices, create_category,
    check_duplicate, get_song_length)
from utils.util_rand import get_letter, get_numbers
from utils.util_device import is_device_active, activate_device, get_devices
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
        'system': SYSTEM,
        'URL':URL,
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
    party = Party.objects.get(pk = pid)
    if get_inactivity(pid,20):
        party.active = False
    
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
        "inactive": not party.active
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
    party = Party.objects.get(pk=pid)

    if get_inactivity(pid,20):
        clean_up_party(party.pk)

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
        party.device_error = activate_device(
            token_info=party.token_info,
            party_id=party.pk,
        )
        party.save()
    print(party.roundNum)
    print(Users.objects.filter(
                    party=party,
                    active=True,
                    hasPicked=False
                ).first().name)
    #song = Songs.objects.filter(category__party=party, state='playing').first()
    #if song:
    #    category = song.category
    #    #if party.roundNum != category.roundNum:
    #    #    party.roundNum = category.roundNum
    #    #    party.save()
    ##else:
    ##    last_played = Songs.objects.filter(
    ##        category__party=party,
    ##        state='played'
    ##        ).order_by('-category__roundNum').first()
    ##    if last_played and party.roundNum != last_played.category.roundNum + 1:
    ##        party.roundNum = last_played.category.roundNum + 1
    ##        party.save()
    ##        print("****************************")
    ##        print("****************************")
    ##        print("****************************")
    ##        print("****************************")
    ##        print("****************************")
    data={
        "success": 'True',
        "inactive" : not party.active
    }

    return JsonResponse(data)


def choose_category(request, pid):
    ''' Allows User with turn in picking state to create a category object

    Parameters:

        - request - web request
        - pid - Primary Key of the Party the User belongs to

    '''

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
    ''' Allows User to create a song Object using a search result object

    Parameters:

        - request - web request
        - pid - Primary Key of the Party the User belongs to

    '''

    party = get_party(pid)
    user = get_user(request, party)
    invalid = False
    if user.hasPicked:
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    
    category = Category.objects.filter(
        party=party, roundNum=party.roundTotal
    ).first()

    if request.method == 'POST':
        form = searchForm(request.POST)
        if form.is_valid():
            result = form.cleaned_data['result']
            if result != '-1':
                search = Searches.objects.filter(uri=result).first()
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
        form = searchForm()
    
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
    search_text = request.GET.get('text', None)
    token = check_token(token_info=party.token_info,party_id=pid)
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
        song_list.append(
            {
            'track_name': track_name,
            'artist': artist_name,
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
    ''' Allows Host to change device, the song time limit or end the session

    Parameters:

        - request - web request
        - pid - Primary Key of the Party the User belongs to

    '''
    if not check_permission(pid, request):
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    party = get_party(pid)
    invalid = False
    get_devices(party)
    if request.method == 'POST':
        form = settingsForm(request.POST, partyObject=party)
        if form.is_valid():
            Devices.objects.filter(party=party).all().delete()
            if ('kill' in request.POST):
                clean_up_party(party.pk)
                return HttpResponseRedirect(reverse('index'))   
            else:
                device = form.cleaned_data['device']
                if device != None:
                    party.deviceID=device.deviceID
                    time = form.cleaned_data['time']
                    party.time = time
                    party.device_error = False
                    party.save()
                    return HttpResponseRedirect(
                        reverse('play', kwargs={'pid':pid})
                    )
                else:
                    invalid = True
    else:
        form = settingsForm(partyObject=party, initial={'time':party.time,})

    context = {
        'party':party,
        'form':form,
        'invalid':invalid,
    }    
    return render(request, 'game/settings.html', context)


def users(request, pid):

    party = get_party(pid)
    user = get_user(request, party)
    users = Users.objects.filter(party=party, active=True).all()
    if request.method == 'POST':
        form = blankForm(request.POST)
        if form.is_valid():
            party = Party.objects.get(pk = pid)
            if ('back' in request.POST):
                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
            elif ('skip' in request.POST):
                if party.roundNum == party.roundTotal:
                    category = Category.objects.filter(
                        party=party,
                        roundNum=party.roundNum
                    ).first()
                    category.full = True
                    category.save()
                    users = Users.objects.filter(party=party, active=True).all()
                    for x in users:
                        x.hasPicked = False
                        x.save()
                    party.state = 'assign'
                    party.save()
                elif party.roundNum > party.roundTotal:
                    lead = Users.objects.filter(
                        party=party,
                        turn='picking',
                        active=True
                    ).first()
                    if lead:
                        lead.turn='picked'
                        lead.save()
                    party.state = 'assign'
                    party.save()
                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
            else:
                for x in users:
                    if (x.sessionID in request.POST):
                        x.active=False
                        x.sessionID = ""
                        x.save()
                        not_picked = Users.objects.filter(
                            party=party,
                            active=True,
                            hasPicked=False
                        ).all()
                        if not not_picked:
                            category = Category.objects.filter(
                                party=party,
                                roundNum=party.roundTotal
                            ).first()
                            category.full = True
                            category.save()
                        return HttpResponseRedirect(
                            reverse('users', kwargs={'pid':pid})
                        )
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
        'isHost':user.isHost,
    }    
    return render(request, 'game/users.html', context)


def play_songs(pid):
    party = Party.objects.get(pk=pid)
    party.thread = True
    if not party.active:
        return
    if party.device_error:
        party.device_error = False
    party.save()
    while (Songs.objects.filter(
            category__party=party,
            category__roundNum=party.roundNum,
            state='not_played',
            category__full=True
        ).all()):
        party = Party.objects.get(pk=pid)
        if not party.active:
            return
        song = Songs.objects.filter(
            category__party=party,
            category__roundNum=party.roundNum,
            state='not_played',
            category__full=True
        ).order_by('order').first()
        if not song.duplicate:
            check_duplicate(party, party.roundNum, song)
            try:   
                token = check_token(token_info=party.token_info, party_id=pid)
                spotify_object = spotipy.Spotify(auth=token)
                activate_device(token_info=party.token_info, party_id=pid)
                spotify_object.start_playback(device_id=party.deviceID, uris=[song.uri])
            except Exception as e:
                party = Party.objects.get(pk=pid)
                if 'Device not found' in str(e):
                    party.device_error = True
                party.thread = False
                party.debug += str(e)
                party.save()
                return
            song.state = 'playing'
            song.startTime = time.time()
            song.save()
            song_length = get_song_length(song)
            threshold = get_like_threshold(party)
            flag = True
            while(time.time() - song.startTime < song_length):
                if Songs.objects.filter(pk=song.pk, likes__lte=threshold).first():
                    break
                if song.duplicate and (time.time() - song.startTime) >= party.time and flag:
                    song.art= "duplicate"
                    song.save()
                    flag = False
        song = Songs.objects.filter(pk=song.pk).first()
        song.state= 'played'
        song.save()
        party = Party.objects.get(pk=pid)
        if not Songs.objects.filter(category__party=party,
                category__roundNum=party.roundNum,state='not_played',
                category__full=True
            ).all():
            reset_user_likes(party)
            set_user_points(party, party.roundNum) 
            party.roundNum += 1
            party.save()
    party = Party.objects.get(pk=pid)
    party.thread = False
    party.save()
    print('EXITING THREAD')

