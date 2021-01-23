from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from party.models import Party, Users, Category, Library, Likes, Songs, Searches, Devices
from party.views import checkToken
from game.forms import blankForm, chooseCategoryForm, searchForm, searchResultsForm, settingsForm
from queue_it_up.settings import DRIVER, SYSTEM, PROD, URL, IP
from datetime import datetime, timedelta, timezone
import spotipy
import time
import random
import os
import threading
import math
import webbrowser


def lobby(request, pid):

    if not checkActive(pid, request):
        return HttpResponseRedirect(reverse('index'))

    p = Party.objects.get(pk = pid)

    inactivity = ((datetime.now(timezone.utc) - p.last_updated).seconds // 60) % 60
    if inactivity >= 20:
        p.active=False
        p.save()
        clean_up_party(p.pk)
    
    if request.method == 'POST':
        form = blankForm(request.POST)

        if form.is_valid():
            if ('code' in request.POST):
                return HttpResponseRedirect(reverse('code', kwargs={'pid':pid}))
            else:
                c = Category(name='Looks Like We Got A Lull',
                             roundNum=0, party=p)
                c.save()
                temp = set()
                libraries = Library.objects.filter(visible=True).exclude(name='Custom').exclude(name='Scattergories')
                for l in libraries:
                    temp.add(l.id)
                p.lib_repo = temp
                p.save()
                if PROD:
                    DRIVER.get('https://www.'+ IP + "/sesh/" + str(pid) +  "/play?user="+ SYSTEM)
                else:
                    webbrowser.open(URL + "/sesh/" + str(pid) +  "/play?user="+ SYSTEM)
                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    else:
        form = blankForm(initial={'text':'blank',})
        p = Party.objects.get(pk = pid)
          
        if p.started:
            return HttpResponseRedirect(reverse('play', kwargs={'pid': pid}))

    guests = Users.objects.filter(party = pid, active=True)
    guests = list(guests)

    u = getUser(request, pid)
    
    if u.isHost:
        access =  True
    else:
        access = False
    
    context = {
        'party':p,
        'guests':guests,
        'access': access,
        'form': form,
        'size': len(guests),
        }
    return render(request, 'game/lobby.html', context)


def update_lobby(request):
    pid = request.GET.get('pid', None)
    p = Party.objects.get(pk = pid)
    inactivity = ((datetime.now(timezone.utc) - p.last_updated).seconds // 60) % 60
    if inactivity >= 20:
        p.active=False
        p.save()
        clean_up_party(p.pk)
    
    guests = Users.objects.filter(party = pid, active=True)
    guests = list(guests)
    
    data = {
        'size': len(guests),
        'started': p.started,
        'inactive': p.active
    }

    return JsonResponse(data)


def code(request, pid):

    if not checkActive(pid, request):
        return HttpResponseRedirect(reverse('index'))
   
    if request.method == 'POST':
        form = blankForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect(reverse('lobby', kwargs={'pid':pid}))
    else:
        form = blankForm(initial={'text':'blank',})

    context = {
                'form' : form,
                }    
    return render(request, 'game/code.html', context)


def play(request, pid):
    p = Party.objects.get(pk = pid)
    url = str(request.get_full_path)
    if 'user=' + SYSTEM in url:
        sys=Users.objects.filter(party=p, name=SYSTEM)
        if not sys:
            sys=Users(party=p, name=SYSTEM, sessionID=request.session.session_key, active=False, refreshRate=3)
            sys.save()

    if not checkActive(pid, request):
        return HttpResponseRedirect(reverse('index'))
    
    u = getUser(request, pid)
           
    if request.method == 'POST':
        form = blankForm(request.POST)
        
        if form.is_valid():
            if ('like' in request.POST):
                u.hasLiked = True
                u.save()
                try:
                    current_song = Songs.objects.get(state='playing', category__party = p)
                    if not current_song.duplicate:
                        l = current_song.likes
                        l.num = l.num + 1
                        l.save()
                except Exception as e:
                    print(e)
            elif ('dislike' in request.POST):
                u.hasLiked = True
                u.save()
                try:
                    current_song = Songs.objects.get(state='playing', category__party = p)
                    if not current_song.duplicate:
                        l = current_song.likes
                        l.num = l.num - 1
                        l.save()
                except Exception as e:
                    print(e)
            
            elif ('results' in request.POST):
                 return HttpResponseRedirect(reverse('round_results', kwargs={'pid':pid}))
            elif('settings' in request.POST):
                return HttpResponseRedirect(reverse('settings', kwargs={'pid':pid}))
            elif('users' in request.POST):
                return HttpResponseRedirect(reverse('users', kwargs={'pid':pid}))
            else:
                if p.state == 'choose_category':
                    return HttpResponseRedirect(reverse('choose_category', kwargs={'pid':pid}))
                if p.state == 'pick_song':
                    return HttpResponseRedirect(reverse('pick_song', kwargs={'pid':pid}))              
    else:
        form = blankForm(initial={'text':'blank',})

    s = Songs.objects.filter(category__party=p, state='playing').first()
    if (s):
        c = s.category
    else:
        s = Songs(art='lull')
        c = Category.objects.filter(party=p, roundNum=0).first()
            
    context = {
        'form':form,
        'party': p,
        'user' : u,
        'category' : c,
        'song' : s,
        'system':SYSTEM
        }
    
    return render(request, 'game/play.html', context)


def update_play(request):
    pid = request.GET.get('pid', None)
    if not checkActive(pid, request):
        inactive = True
    else:
        inactive = False
    p = Party.objects.get(pk = pid)
    u = getUser(request, pid)

    s = Songs.objects.filter(category__party=p, state='playing').first()
    if (s):
        c = s.category
    else:
        s = Songs(art='lull')
        c = Category.objects.filter(party=p, roundNum=0).first()

    party = {
		"device_error" : str(p.device_error),
		"name" : p.name,
		"state": p.state,
		"joinCode" : p.joinCode,
        "inactive": inactive
	}
    user={
	    "isHost":str(u.isHost),
		"hasPicked": str(u.hasPicked),
		"turn": u.turn,
		"hasLiked": str(u.hasLiked),
		"user": u.pk
	}
    try:
        leader = c.leader.name
    except:
        leader = ""
    category={
		"name": c.name,
		"leader": leader,
	}
    try:
        song_user = s.user.pk
    except:
        song_user = -1

    song= {
		"name": s.name,
		"link": s.link,
		"user": song_user,
		"art": s.art
	}
    data = {
        'party': party,
        'user' : user,
        'category' : category,
        'song' : song
    }
    return JsonResponse(data)


def update_game(request):
    pid = request.GET.get('pid', None)
    if not checkActive(pid, request):
        inactive = True
    else:
        inactive = False
    
    p = Party.objects.get(pk = pid)
    inactivity = ((datetime.now(timezone.utc) - p.last_updated).seconds // 60) % 60
    if inactivity >= 20:
        p.active=False
        p.save()
        clean_up_party(p.pk)
    if p.state == 'assign':
        lead = Users.objects.filter(party=p, turn='not_picked', active=True).first()
        if lead:
            lead.turn = 'picking'
            lead.save()
            p.state = 'choose_category'
            p.save()
        else:
            users = Users.objects.filter(party=p, active=True)
            for user in users:
                user.turn = 'not_picked'
                user.save()
            x = list(users)
            lead = x[0]
            lead.turn = 'picking'
            lead.save()
            p.state = 'choose_category'
            p.save()        
        if not p.started:
            p.started = True
            p.save()    

    if  p.state == 'pick_song' and not Users.objects.filter(party=p, hasPicked=False, active=True):
        p.state = 'assign'
        p.save()
        users = Users.objects.filter(party=p, active=True)
        for x in users:
            x.hasPicked = False
            x.save()  
    if p.state == 'choose_category' and not Users.objects.filter(party=p, turn='picking', active=True):
        lead = Users.objects.filter(party=p, turn='not_picked', active=True).first()
        if lead:
            lead.turn = 'picking'
            lead.save()
        else:
            p.state = 'assign'
            p.save()

    if not p.device_error:
        if not p.thread and Songs.objects.filter(category__party=p, category__roundNum = p.roundNum, state='not_played', category__full=True):
            t = threading.Thread(target=playMusic, args=(pid,))
            t.start()
    else:
        p.device_error = not is_device_active(p.pk)
        p.save()

    s = Songs.objects.filter(category__party=p, state='playing').first()
    if s:
        c = s.category
        if p.roundNum != c.roundNum:
            p.roundNum = c.roundNum
            p.save()
    else:
        n = Songs.objects.filter(category__party=p, state='played').order_by('-category__roundNum')
        if n:
            n = list(n)
            if p.roundNum != n[0].category.roundNum + 1:
                p.roundNum = n[0].category.roundNum + 1
                p.save()
    data={
        "success": 'True',
        "inactive" : inactive
        }

    return JsonResponse(data)


def chooseCat(request, pid):

    if not checkActive(pid, request):
        return HttpResponseRedirect(reverse('index'))
    
    invalid=False
    ARTIST='Songs by this Artist'
    p = Party.objects.get(pk=pid)
    u = getUser(request, pid)

    if u.turn != 'picking':
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))

    showCustom = False
    if request.method != 'POST' and p.indices is None:
        num = 12
        if len(p.lib_repo) < num:
            num = len(p.lib_repo)
        p.indices = get_numbers(num, len(p.lib_repo)) 
        p.save() 
    repo = set()
    list_repo = list(p.lib_repo)
    for i in p.indices:
        repo.add(list_repo[int(i)])
        
    if request.method == 'POST':
        form = chooseCategoryForm(request.POST, repo=repo)
        if form.is_valid():
            if ( 'back' in request.POST):
                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
            else:
                try:
                    p.indices = None
                    if not form.cleaned_data['cat_choice'].special:
                        choice_pk = str(form.cleaned_data['cat_choice'].pk)
                        p.lib_repo.remove(choice_pk)   
                    p.save()
                    choice = form.cleaned_data['cat_choice'].display
                    if choice != 'Custom' and choice != ARTIST: 
                        createCategory(
                                        choice=choice,
                                        request=request,
                                        p=p,
                                        sc_type=form.cleaned_data['scatt_radio']
                        )
                        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
                    elif choice == ARTIST:
                        if form.cleaned_data['artist'] != '':
                            createCategory(
                                choice='Songs by ' + form.cleaned_data['artist'],
                                request=request,
                                p=p
                            )
                            return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
                    else:
                        showCustom = True

                        if form.cleaned_data['custom'] != '':
                            createCategory(
                                choice=form.cleaned_data['custom'],
                                request=request,
                                p=p
                            )
                            l = Library(name=form.cleaned_data['custom'])
                            l.save()
                            return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
                except Exception as e:
                    print(e)
                    invalid=True
    else:
        form = chooseCategoryForm(repo=repo, initial={
                                           'cat_choice':'',
                                           'custom':'',
                                           }
        )
    context = {
        'form':form,
        'showCustom':showCustom,
        'invalid':invalid,
        }
    
    return render(request, 'game/chooseCat.html', context)


def createCategory(choice, request, p, sc_type=None):

    u = getUser(request, p)
    u.turn = 'has_picked'
    u.save()

    if choice == 'Scattergories':
        choice =  sc_type + ' Names that Begin with the Letter ' + getLetter()
    
    c = Category(name = choice,
                 roundNum = p.roundTotal + 1,
                 party = p,
                 leader = u,
                )
    c.save()

    p.state = 'pick_song'
    p.roundTotal = p.roundTotal + 1
    p.save()


def pickSong(request, pid):

    if not checkActive(pid, request):
        return HttpResponseRedirect(reverse('index'))
    
    invalid = False
    p = Party.objects.get(pk=pid)
    u = getUser(request, p)

    if u.hasPicked:
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    
    c = Category.objects.filter(party=p, roundNum=p.roundTotal).first()

    if request.method == 'POST':
        form = searchForm(request.POST)

        if form.is_valid():
            if ( 'back' in request.POST):
                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
            else:
                token = checkToken(p.token_info, pid)
                if token is None:
                    token = p.token
                spotifyObject = spotipy.Spotify(auth=token)               
                search = form.cleaned_data['search']
                # choice =  form.cleaned_data['choice_field']
                if search != "":
                # if int(choice) == 1: #Search for Track
                    searchResults = spotifyObject.search(search, 15, 0, 'track')
                    tracks = searchResults['tracks']['items'] 
                    for x in tracks:
                        try:
                            albumArt = x['album']['images'][0]['url']
                        except:
                            albumArt=""
                        artistName = x['artists'][0]['name']  
                        trackName = x['name']
                        trackURI = x['uri']
                        trackDuration = x['duration_ms']
                        url = x['external_urls']['spotify']
                        trackName = (trackName[:255] + '..') if len(trackName) > 255 else trackName
                        s = Searches(
                                        name = trackName + ", " + artistName,
                                        uri=trackURI,
                                        art=albumArt,
                                        party=p,
                                        user=u,
                                        link=url,
                                        duration=trackDuration
                                    )
                        s.save()                    
                    return HttpResponseRedirect(reverse('search_results', kwargs={'pid':pid}))
                else:
                    invalid=True
    else:
        form = searchForm(initial={'search':'',})
    
    context = {
        'form':form,
        'category':c,
        'invalid':invalid
        }
    return render(request, 'game/pickSong.html', context)


def searchResults(request, pid):

    if not checkActive(pid, request):
        return HttpResponseRedirect(reverse('index'))

    invalid = False
    
    p = Party.objects.get(pk=pid)
    u = getUser(request, p)

    if u.hasPicked:
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    
    c = Category.objects.filter(party=p, roundNum=p.roundTotal).first() 
    try:
        isArtist = (list(Searches.objects.filter(party=p).filter(user=u))[0].art == None)
    except:
        isArtist = True
        
    if request.method == 'POST':
        form = searchResultsForm(request.POST, partyObject=p, userObject=u)
        if form.is_valid():
            if ('add2q' in request.POST):
                search = form.cleaned_data['results']
                if search != None:
                    l = Likes()
                    l.save()
                    s = Songs(
                              name=search.name,
                              uri=search.uri,
                              art=search.art,
                              user=u,
                              category=c,
                              played=False,
                              order=random.randint(1,101),
                              state='not_played',
                              likes=l,
                              link=search.link,
                              duration=search.duration,
                    )
                    s.save()
                    u.hasPicked = True
                    u.save()
                    Searches.objects.filter(user=u, party=p).delete()

                    not_picked = Users.objects.filter(party=p, active=True, hasPicked=False)
                    if not not_picked:
                        c.full = True
                        c.save()

                    return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
                else:
                    invalid = True

            elif ('back' in request.POST):
                Searches.objects.filter(user=u).filter(party=p).delete()
                return HttpResponseRedirect(reverse('pick_song', kwargs={'pid':pid}))
    else:
        form = searchResultsForm(partyObject=p, userObject=u, initial={'results':''})
   
    albumSearch = list(Searches.objects.filter(party=p, user=u).order_by('pk'))
        
    context = {
               'form':form,
               'isArtist':isArtist,
               'invalid':invalid,
               'albumSearch':albumSearch
               }
        
    return render(request, 'game/searchResults.html', context)

def roundResults(request, pid):

    if not checkActive(pid, request):
        return HttpResponseRedirect(reverse('index'))

    p = Party.objects.get(pk=pid)
    if p.roundNum > 1:
        songs = list(Songs.objects.filter(category__roundNum = p.roundNum - 1, category__party = p).order_by('-likes__num'))
        category = songs[0].category.name
    else:
        category = "No Results Yet"
        songs = []
    
    if request.method == 'POST':
        form = blankForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    else:
        form = blankForm(initial={'text':'blank',})

    context = {
                'form' : form,
                'songs': songs,
                'category': category,
                }    
    return render(request, 'game/roundResults.html', context)


def settings(request, pid):

    if not checkActive(pid, request):
        return HttpResponseRedirect(reverse('index'))

    if not checkPermission(pid, request):
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    
    invalid = False
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

    if not checkActive(pid, request):
        return HttpResponseRedirect(reverse('index'))

    p = Party.objects.get(pk = pid)
    u = getUser(request, p)
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
              'has_picked':'Yes'
              }
    
    context = {
                'form' : form,
                'users':users,
                'decode':decode,
                'isHost':isHost,
                
                }    
    return render(request, 'game/users.html', context)


def getUser(request, p):
    
    sk = request.session.session_key
    try:
        u = Users.objects.get(sessionID = sk, party = p)
    except:
        return HttpResponseRedirect(reverse('index'))
    return u


def checkActive(pid, request):
    try:
        p = Party.objects.get(pk = pid)
        users = Users.objects.filter(party=p, active=True)
        if not p.active:
            return False
        elif not users :
            return False
        else:
            u = getUser(request, p)
            if u.name != SYSTEM:
                return u.active
            else:
                return True
    except:
        return False


def getLetter():                                    
    rand = random.randint(65,90)
    letter = chr(rand)
    return letter


def get_numbers(amount, length):
    l = set()
    while len(l) < amount:
        l.add(random.randint(0, length - 1))
    return l


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


def playMusic(pid):
    p = Party.objects.get(pk = pid)
    p.thread = True
    if not p.active:
        return
    if p.device_error:
        p.device_error = False
    p.save()
    rN = p.roundNum
    token = checkToken(p.token_info, pid)
    if token is None:
        token = p.token
    spotifyObject = spotipy.Spotify(auth=token)
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
                    
                    token = checkToken(p.token_info, pid)
                    if token != None:
                        spotifyObject = spotipy.Spotify(auth=token)
                    activate_device(p.id)
                    spotifyObject.start_playback(device_id=p.deviceID , uris=ls)
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
                        if Songs.objects.filter(pk=song.pk, likes__num__lte=num):
                            break
                        if song.duplicate and (time.time() - song.startTime) >= p.time and flag:
                            song.art= "duplicate"
                            song.save()
                            flag = False
                        continue
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
            u.points = u.points + s.likes.num
            u.save()   
        rN = rN + 1
    p = Party.objects.get(pk = pid)
    p.thread=False
    p.save()
    print('EXITING THREAD')

def activate_device(pid):
    p = Party.objects.get(pk = pid)
    token = checkToken(p.token_info, pid)
    if token is None:
        token = p.token
    spotifyObject = spotipy.Spotify(auth=token)
    deviceResults = spotifyObject.devices()
    deviceResults = deviceResults['devices']
    flag = True
    for device in deviceResults:
        if device["id"] == p.deviceID:
            if not device["is_active"]:
                spotifyObject.transfer_playback(device_id=p.deviceID, force_play=False)
            else:
                flag = False
    if flag:
        p.debug = p.debug + " **!!!** Device Not Found"
        p.save()


def is_device_active(pid):
    p = Party.objects.get(pk = pid)
    token = checkToken(p.token_info, pid)
    if token is None:
        token = p.token
    spotifyObject = spotipy.Spotify(auth=token)
    deviceResults = spotifyObject.devices()
    deviceResults = deviceResults['devices']
    flag = True
    for device in deviceResults:
        if device["id"] == p.deviceID:
            return(True)
    return False

def clean_up_party(pid):
    p = Party.objects.get(pk=pid)
    p.token = ""
    p.token_info = ""
    p.url = ""
    p.url_open = ""
    p.deviceID = ""
    p.save()

