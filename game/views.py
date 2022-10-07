from django.shortcuts import render
from django.urls import reverse
from background_task import background
from utils.util_auth import check_token
from utils.util_user import (get_user, check_permission, assign_leader,
     reset_users, set_user_points, reset_user_likes, get_like_total)
from utils.util_party import (get_party, clean_up_party, get_inactivity,
     set_lib_repo, get_results, get_totals, get_category_choices,
     create_category, check_duplicate, wait_for_song)
from utils.util_device import get_active_device
from utils.util_song import get_bg_color
from django.http import HttpResponseRedirect, JsonResponse
from party.models import Party, Users, Category, Songs, Searches, Devices
from game.forms import (blankForm, chooseCategoryForm, searchForm,
     settingsForm)
import spotipy
import time
import threading
import random
from queue_it_up.settings import URL, QDEBUG


def lobby(request, pid):
    ''' Gets Users in Party and Displays them. The Party host has the ability
    to start the party by submitting the form. Submitting the form launches a
    browser window on the system and sets the party to started.

    Parameters:

        - request - web request
        - pid - Primary Key of the Party the User belongs to

    '''
    party = get_party(pid)
    if party == -1:
        return HttpResponseRedirect(reverse('index'))
    if get_inactivity(pid,19):
        clean_up_party(party.pk)
    if request.method == 'POST':
        form = blankForm(request.POST)
        if form.is_valid():
            category = Category(name='Looks Like We Got A Lull', party=party)
            category.save()
            party.lib_repo = set_lib_repo()
            party.started = True
            party.save()
            task = threading.Thread(target=call_task, args=(pid,))
            task.start()
            return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    else:
        form = blankForm(initial={'text':'blank',})
        party = Party.objects.get(pk=pid)
        if party.started:
            return HttpResponseRedirect(reverse('play', kwargs={'pid': pid}))
    users = Users.objects.filter(party=pid, active=True).all()
    names=[]
    for user in users:
        names.append(user.name)
    current_user = get_user(request, pid)
    if current_user.isHost:
        device = get_active_device(party)
    else:
        device = {}
    context = {
        'party':party,
        'names':names,
        'access':current_user.isHost,
        'form':form,
        'URL':URL,
        'device': device
    }
    return render(request, 'game/lobby.html', context)


def update_lobby(request):
    ''' Ajax request to update the users on the lobby page. Returns an updated
    party size, list of names, and whether the party is started or inactive. 

    Parameters:

        - request - web request

    '''
    pid = request.GET.get('pid', None)
    party = Party.objects.get(pk = pid)
    if get_inactivity(pid,19):
        clean_up_party(party.pk)
    users = Users.objects.filter(party=pid, active=True).all()
    names=[]
    for user in users:
        names.append(user.name)
    data = {
        'size': users.count(),
        'started': party.started,
        'names': names,
        'inactive': party.active
    }
    return JsonResponse(data)


def call_task(pid):
    ''' Thread used to run background task, prevents delay in redirect while
    calling the task

    Parameters:
        - pid - Primary Key of the Party the User belongs to

    '''
    run_game.now(pid)


def play(request, pid):
    ''' Gets the song playing and displays it with the category and party info.
    Form Post will increment/decrement the playing song's likes.

    Parameters:

        - request - web request
        - pid - Primary Key of the Party the User belongs to

    '''
    party = get_party(pid)
    user = get_user(request, pid)
    if party == -1 or user == -1:
        return HttpResponseRedirect(reverse('index'))
    song = Songs.objects.filter(category__party=party, state='playing').first()
    if song:
        category = song.category
    else:
        song = Songs(art='lull')
        category = Category.objects.filter(party=party, roundNum=0).first()
    
    last_category = Category.objects.filter(
        party=party, roundNum=party.roundTotal
    ).first()
    full = False
    if last_category:
        full = last_category.full

    results = get_results(party)
    totals = get_totals(party)

    if user.isHost:
        device = get_active_device(party)
    else:
        device = {}

    context = {
        'party': party,
        'user' : user,
        'category' : category,
        'song' : song,
        'results': results,
        'totals': totals,
        'URL': URL,
        'full': full,
        'device':device
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
    party = Party.objects.get(pk=pid)
    if get_inactivity(pid,19):
        party.active = False
    
    user = get_user(request, pid)

    song = Songs.objects.filter(category__party=party, state='playing').first()
    if song:
        category = song.category
    else:
        song = Songs(art='lull')
        category = Category.objects.filter(party=party, roundNum=0).first()
    
    last_category = Category.objects.filter(
        party=party, roundNum=party.roundTotal
    ).first()
    full = False
    if last_category:
        full = last_category.full

    results = get_results(party)
    totals = get_totals(party)
 
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
        "hasSkip" : str(user.hasSkip),
		"user": user.pk
	}
    try:
        leader = category.leader.name
    except Exception:
        leader = ""
    category_info={
		"name": category.name,
		"leader": leader,
        "full":full,
	}
    try:
        song_user = song.user.pk
    except Exception:
        song_user = -1

    song_info= {
		"name": song.name,
        "title": song.title,
        "artist": song.artist,
		"link": song.link,
		"user": song_user,
		"art": song.art,
        "color": song.color
	}
    data = {
        'party': party_info,
        'user' : user_info,
        'category': category_info,
        'song': song_info,
        'results': results,
        'totals': totals
    }
    return JsonResponse(data)


def update_like(request):
    ''' Ajax call to increment or Decrement the like field of a Song object
        based on the request. Prevents user from liking one song multiple times.

    Parameters:

        - request - web request

    '''
    pid = request.GET.get('pid', None)
    like = request.GET.get('like', None)
    action = request.GET.get('action', None)
    user = get_user(request, pid)   
    
    if like == 'true':
        if action == 'like': 
            user.hasLiked = True
            user.hasSkip = False
        else:
            user.hasLiked = False
            user.hasSkip = False
    else:
        if action == 'dislike':
            user.hasLiked = False
            user.hasSkip = True
        else:
            user.hasLiked = False
            user.hasSkip = False
    user.save()
    print(QDEBUG,user.name, ': Set User Like: ', user.hasLiked, ' Set User Dislike: ', user.hasSkip)
    data = {}
    return JsonResponse(data)


@background()
def run_game(pid):
    ''' Background Task to update the game logic and trigger the song thread 

    Parameters:

        - pid - primary key of party

    '''
    while(Party.objects.filter(pk=pid, active=True).first()):
        if get_inactivity(pid,19):
            clean_up_party(pid)

        if Party.objects.filter(pk=pid,active=True,state='assign').first() or (
            Party.objects.filter(pk=pid,active=True,state='choose_category'
                ).first() 
            and not 
            Users.objects.filter(turn='picking',party__pk=pid,active=True
                ).first()
           ):
            party = Party.objects.get(pk=pid)
            assign_leader(party)
            party.state = 'choose_category'
            party.save()
            print(QDEBUG,'Set state to choose category: ', party.state)
                    
        if Party.objects.filter(pk=pid,active=True,state='pick_song').first() \
                and not \
                Users.objects.filter(hasPicked=False,party__pk=pid,active=True
            ).all():
            party = Party.objects.get(pk=pid)
            category = Category.objects.filter(
                party=party,roundNum=party.roundTotal).first()
            category.full = True
            category.save()
            print(QDEBUG,'Set Category to Full: ', category.full)
            party.state = 'assign'
            party.save()
            print(QDEBUG,'Set state to assign: ', party.state)
            reset_users(party) 
        
        party = Party.objects.get(pk=pid)
        if Party.objects.filter(
                pk=pid,
                active=True,
                device_error=False,
                thread=False
            ).first() and \
            Songs.objects.filter(
                category__party__pk=pid,
                category__roundNum=party.roundNum,
                state='not_played',
                category__full=True
          ):
            thread = threading.Thread(target=play_songs, args=(pid,))
            thread.start()
            party = Party.objects.get(pk=pid)
            party.thread = True
            party.save()
            print(QDEBUG,'Set Thread to True: ', party.thread)

    print(QDEBUG, "exiting task: ", Party.objects.filter(pk=pid, active=True).first())


def choose_category(request, pid):
    ''' Allows User with turn in picking state to create a category object

    Parameters:

        - request - web request
        - pid - Primary Key of the Party the User belongs to

    '''

    party = get_party(pid)
    user = get_user(request, pid)
    if party == -1 or user == -1:
        return HttpResponseRedirect(reverse('index'))
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
                print(QDEBUG,'Set state to pick_song: ', party.state, ' Round Total: ',
                    party.roundTotal)
                party = Party.objects.get(pk=pid)
                remaining_users = Users.objects.filter(
                    party=party,
                    active=True,
                    turn='not_picked'
                ).all()
                if not remaining_users:
                    user.turn = 'has_picked_last'
                else:
                    user.turn = 'has_picked'
                user.save()
                print(QDEBUG,'Set Leader Turn to: ',user.name, ' - ', user.turn)
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
    if party == -1 or user == -1:
        return HttpResponseRedirect(reverse('index'))
    invalid = False
    if user.hasPicked or party.state != 'pick_song':
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    
    category = Category.objects.filter(
        party=party, roundNum=party.roundTotal
    ).first()

    if request.method == 'POST':
        form = searchForm(request.POST)
        if form.is_valid():
            result = form.cleaned_data['result']
            picked_song = Songs.objects.filter(
                user=user, category=category
                ).first()
            if picked_song:
                user.hasPicked = True
                user.save()
                print(
                    QDEBUG,'Set User has Picked: ',user.name,'-',user.hasPicked
                    )
                return HttpResponseRedirect(
                    reverse('play', kwargs={'pid':pid})
                )
            elif result != '-1':
                search = Searches.objects.filter(uri=result).first()
                song = Songs(
                    name=search.name,
                    title = search.title,
                    artist = search.artist,
                    uri=search.uri,
                    art=search.art,
                    user=user,
                    category=category,
                    played=False,
                    order=random.randint(1,101),
                    state='not_played',
                    link=search.link,
                    duration=search.duration,
                )
                song.save()
                print(QDEBUG, "SONG: ", song.title, song.artist)
                thread = threading.Thread(target=get_bg_color, args=(song.id,))
                thread.start()
                Searches.objects.filter(user=user, party=party).delete()
                user.hasPicked = True
                user.save()
                print(
                    QDEBUG,'Set User has Picked: ',user.name,'-',user.hasPicked
                    )
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
            track_name[:255] + '..'
        ) if len(track_name) > 255 else track_name
        if not current or current.uri != track_uri:
            search = Searches(
                name = track_name + ", " + artist_name,
                title = track_name,
                artist = artist_name,
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
    device = get_active_device(party)
    if request.method == 'POST':
        form = settingsForm(request.POST, partyObject=party)
        if form.is_valid():
            Devices.objects.filter(party=party).all().delete()
            if ('kill' in request.POST):
                clean_up_party(party.pk)
                return HttpResponseRedirect(reverse('index'))   
            else:
                time = form.cleaned_data['time']
                party.time = time
                party.device_error = False
                party.save()
                return HttpResponseRedirect(
                    reverse('start_party', kwargs={'pid':pid})
                )
    else:
        form = settingsForm(partyObject=party, initial={'time':party.time,})

    context = {
        'party':party,
        'form':form,
        'device':device
    }    
    return render(request, 'game/settings.html', context)


def users(request, pid):

    party = get_party(pid)
    current_user = get_user(request, party)
    if party == -1 or current_user == -1:
        return HttpResponseRedirect(reverse('index'))
    users = Users.objects.filter(party=party, active=True).all()
    if request.method == 'POST':
        form = blankForm(request.POST)
        if form.is_valid():
            party = Party.objects.get(pk=pid)
            if ('skip' in request.POST):
                if party.roundNum == party.roundTotal:
                    category = Category.objects.filter(
                        party=party,
                        roundNum=party.roundNum
                    ).first()
                    category.full = True
                    category.save()
                    reset_users(party)
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
                for user in users:
                    if (user.sessionID in request.POST):
                        user.active=False
                        user.sessionID = ""
                        user.save()
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
        'party':party,
        'form' : form,
        'users':users,
        'decode':decode,
        'isHost':current_user.isHost,
    }    
    return render(request, 'game/users.html', context)


def play_songs(pid):
    party = Party.objects.get(pk=pid)
    if party.device_error:
        party.device_error = False
        party.save()
        print(QDEBUG,'Reset Device Error: ', party.device_error)
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
                spotify_object.start_playback(
                    device_id=party.deviceID, uris=[song.uri])
            except Exception as e:
                party = Party.objects.get(pk=pid)
                if 'Device not found' in str(e):
                    party.device_error = True
                party.thread = False
                party.debug += str(e)
                party.save()
                song.duplicate = False
                song.save()
                return
            song.state = 'playing'
            song.startTime = time.time()
            song.save()
            print(QDEBUG,'Set Song to playing: ', song.name, ' - ', song.state)
            wait_for_song(song)
        song = Songs.objects.filter(pk=song.pk).first()
        song.state = 'played'
        song.likes = get_like_total(song) 
        song.save()
        print(QDEBUG,'Set Song to played: ', song.name, ' - ', song.state)
        reset_user_likes(party)
        party = Party.objects.get(pk=pid)
        if not Songs.objects.filter(category__party=party,
                category__roundNum=party.roundNum,state='not_played',
                category__full=True
            ).all():
            set_user_points(party, party.roundNum) 
            party.roundNum += 1
            party.save()
            print(QDEBUG,'Increment Round Number: ', party.roundNum)
    party = Party.objects.get(pk=pid)
    party.thread = False
    party.save()
    print(QDEBUG,'Set Thread Flag to False: ', party.thread)
    print(QDEBUG,'EXITING THREAD')

