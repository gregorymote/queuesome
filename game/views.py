from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from party.models import Party
from party.models import Users
from party.models import Category
from party.models import Library
from party.models import Likes
from party.models import Songs
from party.models import Searches
from party.models import Devices
from party.views import checkToken
from game.forms import blankForm
from game.forms import chooseCategoryForm
from game.forms import searchForm
from game.forms import searchResultsForm
from game.forms import settingsForm

import spotipy
import time
import random
import os
import threading

def lobby(request, pid):

    if not checkActive(pid):
        return HttpResponseRedirect(reverse('start'))

    p = Party.objects.get(pk = pid)
    
    if request.method == 'POST':
        form = blankForm(request.POST)

        if form.is_valid():
            if ('code' in request.POST):
                return HttpResponseRedirect(reverse('code', kwargs={'pid':pid}))
            else:
                c = Category(name='Looks Like We Got A Lull',
                             roundNum=0, party=p)
                c.save()
    ##            spotifyObject = spotipy.Spotify(auth=p.token)
    ##            searchResults = spotifyObject.search("Kickstart my heart", 1, 0, 'track')
    ##            tracks = searchResults['tracks']['items']
    ##            ls = []
    ##            for x in tracks:
    ##                ls.append(x['uri'])
    ##            try:    
    ##                spotifyObject.start_playback(device_id=p.deviceID , uris=ls)
    ##                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    ##            except:
                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    else:
        form = blankForm(initial={'text':'blank',})
        p = Party.objects.get(pk = pid)
          
        if p.started:
            return HttpResponseRedirect(reverse('play', kwargs={'pid': pid}))

    guests = Users.objects.filter(party = pid)
    guests = list(guests)

    u = getUser(request, pid)
    
    if u.isHost:
        access =  True
    else:
        access = False
    
    party_name = guests[0].party.name
    context = {
        'party':p,
        'guests':guests,
        'access': access,
        'form': form,
        }

    
    return render(request, 'game/lobby.html', context)


def code(request, pid):

    if not checkActive(pid):
        return HttpResponseRedirect(reverse('start'))
   
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

    if not checkActive(pid):
        return HttpResponseRedirect(reverse('start'))
    
    p = Party.objects.get(pk = pid)
    u = getUser(request, pid)
    
    if p.state == 'assign' and u.isHost:
        x = Users.objects.filter(party=p, turn='not_picked')
        print('****')
        print(x)
        print('****')
        
        if x:
            x = list(x)
            lead = x[0]
            lead.turn = 'picking'
            lead.save()
            p.state = 'choose_category'
            p.save()
            
        else:
            users = Users.objects.filter(party=p)
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
    
    if len(list(Users.objects.filter(party=p, hasPicked=False))) == 0 and p.state == 'pick_song':
        
        p.state = 'assign'
        p.save()
        
        users = Users.objects.filter(party = p)
        for x in users:
            x.hasPicked = False
            x.save()

        isPlaying = Songs.objects.filter(category__party=p, state='playing')
        if not isPlaying:
            t = threading.Thread(target=playMusic, args=(pid,))
            t.start()
            
    if p.state == 'choose_category' and Users.objects.filter(party=p, turn='not_picked') and not Users.objects.filter(party=p, turn='picking'):
        x = Users.objects.filter(party=p, turn='not_picked')
        if x:
            x = list(x)
            lead = x[0]
            lead.turn = 'picking'
            lead.save()
        
    if request.method == 'POST':
        form = blankForm(request.POST)
        
        if form.is_valid():
            if ('like' in request.POST):
                u.hasLiked = True
                u.save()
                try:
                    current_song = Songs.objects.get(state='playing', category__party = p)
                    l = current_song.likes
                    l.num = l.num + 1
                    l.save()
                except Exception as e:
                    print(e)
            elif ('results' in request.POST):
                 return HttpResponseRedirect(reverse('round_results', kwargs={'pid':pid}))
            elif('settings' in request.POST):
                return HttpResponseRedirect(reverse('settings', kwargs={'pid':pid}))
            else:
                if p.state == 'choose_category':
                    return HttpResponseRedirect(reverse('choose_category', kwargs={'pid':pid}))
                if p.state == 'pick_song':
                    return HttpResponseRedirect(reverse('pick_song', kwargs={'pid':pid}))
              
    else:
        form = blankForm(initial={'text':'blank',})

    try:
        s = Songs.objects.get(category__party=p, state='playing')
        c = s.category

        if p.roundNum != c.roundNum:
            p.roundNum = c.roundNum
            p.save()
        
    except:
        s = Songs(art='lull')
        c = Category.objects.get(party=p, roundNum=0)
        n = Songs.objects.filter(category__party=p, state='played').order_by('-category__roundNum')
        if len(list(n)) != 0:
            if p.roundNum != n[0].category.roundNum + 1:
                p.roundNum = n[0].category.roundNum + 1
                p.save()
        
    context = {
        'form':form,
        'party': p,
        'user' : u,
        'category' : c,
        'song' : s,
        }
    
    return render(request, 'game/play.html', context)



def chooseCat(request, pid):

    if not checkActive(pid):
        return HttpResponseRedirect(reverse('start'))
    
    default = ''
    p = Party.objects.get(pk=pid)
    u = getUser(request, pid)

    if u.turn != 'picking':
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))

    showCustom = False
    
    if request.method == 'POST':
        form = chooseCategoryForm(request.POST)

        if form.is_valid():

            if form.cleaned_data['cat_choice'].name != 'custom': 
                createCategory(form.cleaned_data['cat_choice'].name, request, p)

                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
            else:
                showCustom = True

                if form.cleaned_data['custom'] != default:
                    createCategory(form.cleaned_data['custom'], request, p)
                    l = Library(name=form.cleaned_data['custom'])
                    l.save()
                    return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    else:

        form = chooseCategoryForm(initial={
                                           'cat_choice':'',
                                           'custom':default,
                                           }
                                  )
    context = {
        'form':form,
        'showCustom':showCustom,
        }
    
    return render(request, 'game/chooseCat.html', context)


def createCategory(choice, request, p):

    u = getUser(request, p)
    u.turn = 'has_picked'
    u.save()
    
    c = Category(name = choice,
                 roundNum = p.roundTotal + 1,
                 party = p,
                 leader = u,
                )
    c.save()

    print("\n\nnew category created for round:" + str(p.roundTotal) +"\n\n")

    p.state = 'pick_song'
    p.roundTotal = p.roundTotal + 1
    p.save()

def pickSong(request, pid):

    if not checkActive(pid):
        return HttpResponseRedirect(reverse('start'))
    
    invalid = False
    p = Party.objects.get(pk=pid)
    u = getUser(request, p)

    if u.hasPicked:
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    
    c = Category.objects.get(party=p, roundNum=p.roundTotal) 

    if request.method == 'POST':
        form = searchForm(request.POST)

        if form.is_valid():
            
            checkToken(p.token_info, pid)
            spotifyObject = spotipy.Spotify(auth=p.token)
            
            search = form.cleaned_data['search']
            choice =  form.cleaned_data['choice_field']
            if search != "":
                if int(choice) == 1: #Search for Track
                    searchResults = spotifyObject.search(search, 5, 0, 'track')
                    tracks = searchResults['tracks']['items'] 
                    for x in tracks:
                        albumArt = x['album']['images'][0]['url']
                        artistName = x['artists'][0]['name']  
                        trackName = x['name']
                        trackURI = x['uri']
                        url = x['external_urls']['spotify']
                        s = Searches(name = trackName + ", " + artistName,
                                     uri=trackURI, art=albumArt, party=p, user=u, link=url)
                        s.save()
                    
                else:
                    searchResults = spotifyObject.search(search, 5, 0, "artist")
                    artists = searchResults['artists']['items']

                    for x in artists:
                        s = Searches(name = x['name'], uri = x['id'], party=p, user=u)
                        s.save()
                    

                return HttpResponseRedirect(reverse('search_results', kwargs={'pid':pid}))
            else:
                invalid = True
    else:

        form = searchForm(initial={'search':'',})
    context = {
        'form':form,
        'category':c,
        'invalid':invalid
        }
    
    return render(request, 'game/pickSong.html', context)

def searchResults(request, pid):

    if not checkActive(pid):
        return HttpResponseRedirect(reverse('start'))

    invalid = False
    
    p = Party.objects.get(pk=pid)
    u = getUser(request, p)

    if u.hasPicked:
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    
    c = Category.objects.get(party=p, roundNum=p.roundTotal) 
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
                
                    s = Songs(name=search.name,
                              uri=search.uri,
                              art=search.art,
                              user=u,
                              category=c,
                              played=False,
                              order=random.randint(1,101),
                              state = 'not_played',
                              likes = l,
                              link=search.link,
                              )
                    s.save()
                    u.hasPicked = True
                    u.save()
                    Searches.objects.filter(user=u).filter(party=p).delete()
                    return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
                else:
                    invalid = True

            elif ('back' in request.POST):
                Searches.objects.filter(user=u).filter(party=p).delete()
                return HttpResponseRedirect(reverse('pick_song', kwargs={'pid':pid}))

            elif('artist' in request.POST):
                checkToken(p.token_info, pid)
                spotifyObject = spotipy.Spotify(auth=p.token)
                search = form.cleaned_data['results']
                if search != None:
                    Searches.objects.filter(user=u).filter(party=p).delete()
                    topTracks = spotifyObject.artist_top_tracks(search.uri)
                    tracks = topTracks['tracks'] 

                    for x in tracks:
                        albumArt = x['album']['images'][0]['url']
                        artistName = x['artists'][0]['name']  
                        trackName = x['name']
                        trackURI = x['uri']
                        s = Searches(name = trackName + ", " + artistName,
                                     uri=trackURI, art=albumArt, party=p, user=u)
                        s.save()
                    
                    return HttpResponseRedirect(reverse('search_results', kwargs={'pid':pid}))
                else:
                    invalid = True
    else:
        form = searchResultsForm(partyObject=p, userObject=u, initial={'results':''})
        
        
    context = {
               'form':form,
               'isArtist':isArtist,
               'invalid':invalid,
               }
        
    return render(request, 'game/searchResults.html', context)

def roundResults(request, pid):

    if not checkActive(pid):
        return HttpResponseRedirect(reverse('start'))

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

    if not checkActive(pid):
        return HttpResponseRedirect(reverse('start'))
    
    invalid = False
    p = Party.objects.get(pk = pid)
    checkToken(p.token_info, pid)
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
        form = settingsForm(request.POST, partyObject=p)

        if form.is_valid():
            
            if ('back' in request.POST):
                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))

            elif ('kill' in request.POST):
                p.active = False
                p.save()
                return HttpResponseRedirect(reverse('start'))
                
            else:
                device = form.cleaned_data['device']
                if device != None:
                    p.deviceID=device.deviceID
                    time = form.cleaned_data['time']
                    p.time = time
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


def getUser(request, p):
    
    sk = request.session.session_key
    try:
        u = Users.objects.get(sessionID = sk, party = p)
    except:
        return HttpResponseRedirect(reverse('start'))
    return u

def checkActive(pid):
    try:
        p = Party.objects.get(pk = pid)
        return p.active
    except:
        return False      

def playMusic(pid):
    
    p = Party.objects.get(pk = pid)
    rN = p.roundNum
    print ('rN:', rN)
    checkToken(p.token_info, pid)
    spotifyObject = spotipy.Spotify(auth=p.token)
    while (Songs.objects.filter(category__party=p, category__roundNum = rN, state='not_played')):
       
        print ('playing music for round:', rN)
        queue = list(Songs.objects.filter(category__party=p, category__roundNum = rN, state='not_played').order_by('order'))
        for song in queue:
            ls = [song.uri]
            try:
                check = checkToken(p.token_info, pid)
                if check != None:
                    spotifyObject = spotipy.Spotify(auth=check)
                spotifyObject.start_playback(device_id=p.deviceID , uris=ls)
                song.state = 'playing'
                song.startTime = time.time()
                song.save()
                while(time.time() - song.startTime < p.time):
                    continue
                song.state= 'played'
                song.save()
            except Exception as e:
                print("***********************")
                print(e)
                print("***********************")
                song.state = "error, not played"
                song.save()
            users = Users.objects.filter(party = p)
            for x in users:
                x.hasLiked = False
                x.save()

        rN = rN + 1
##    searchResults = spotifyObject.search("Rockabye Baby!", 1, 0, "artist")
##    artist = searchResults['artists']['items'][0]['id']
##    search = spotifyObject.artist_top_tracks(artist, country='US')
##    tracks = search['tracks']
##    ls = []
##    for track in tracks:
##        ls.append(track['uri'])
##    spotifyObject.start_playback(device_id=p.deviceID , uris=ls)
##    spotifyObject.shuffle(True, device_id = p.deviceID)
    print('EXITING THREAD')
