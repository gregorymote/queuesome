from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from party.models import Party
from party.models import Users
from party.models import Category
from party.models import Songs
from party.models import Searches
from game.forms import blankForm
from game.forms import chooseCategoryForm
from game.forms import searchForm
from game.forms import searchResultsForm

import spotipy
import time
import random
import os
import threading

def lobby(request, pid):

    p = Party.objects.get(pk = pid)
    
    if request.method == 'POST':
        form = blankForm(request.POST)

        if form.is_valid():
            c = Category(name='Looks Like We Got A Lull on Our Hands',
                         roundNum=0, party=p)
            c.save()
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
        'guests':guests,
        'party_name': party_name,
        'access': access,
        'form': form,
        }

    
    return render(request, 'game/lobby.html', context)



def play(request, pid):

    p = Party.objects.get(pk = pid)
    u = getUser(request, pid)
    print('roundNum:', p.roundNum)
    print('roundTotal:', p.roundTotal)
    print('state:', p.state)
    
    if p.state == 'assign':
        x = Users.objects.filter(party=p, turn='not_picked')
        
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
        
        q = Category.objects.filter(party=p, roundNum=p.roundTotal)

        if u.sessionID == lead.sessionID:
            c = Category(name = lead.name + " is Picking the Category",
                         roundNum = p.roundTotal + 1,
                         party = p,
                         leader = lead,
                        )
            c.save()
            p.roundTotal = p.roundTotal + 1
            p.save()
            print("\n\nnew category created for round:" + str(p.roundTotal) +"\n\n")
           

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
        
    if request.method == 'POST':
        form = blankForm(request.POST)

        if form.is_valid():
            if p.state == 'choose_category':
                return HttpResponseRedirect(reverse('choose_category', kwargs={'pid':pid}))
            if p.state == 'pick_song':
                return HttpResponseRedirect(reverse('pick_song', kwargs={'pid':pid}))
    else:
        form = blankForm(initial={'text':'blank',})

    try:
        s = Songs.objects.get(category__party=p, state='playing')
        c = s.category
        p.roundNum = c.roundNum
        p.save()
        
    except:
        s = Songs(art='lull')
        c = Category.objects.get(party=p, roundNum=0)
        n = Category.objects.filter(party=p).order_by('-roundNum')
        if len(list(n)) != 0:
            p.roundNum = n[0].roundNum
            print('most recent round num', n[0].roundNum)
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
    default = ''
    p = Party.objects.get(pk=pid)
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

    c = Category.objects.get(party=p, roundNum=p.roundTotal)
    c.name = choice
    c.save()

    p.state = 'pick_song'
    p.save()

def pickSong(request, pid):
    
    p = Party.objects.get(pk=pid)
    u = getUser(request, p)

    if u.hasPicked:
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    
    c = Category.objects.get(party=p, roundNum=p.roundTotal) 

    if request.method == 'POST':
        form = searchForm(request.POST)

        if form.is_valid():
            

            spotifyObject = spotipy.Spotify(auth=p.token)
            
            search = form.cleaned_data['search']
            choice =  form.cleaned_data['choice_field']
            
            if int(choice) == 1: #Search for Track
                searchResults = spotifyObject.search(search, 5, 0, 'track')
                tracks = searchResults['tracks']['items'] 
                for x in tracks:
                    albumArt = x['album']['images'][0]['url']
                    artistName = x['artists'][0]['name']  
                    trackName = x['name']
                    trackURI = x['uri']
                    s = Searches(name = trackName + ", " + artistName,
                                 uri=trackURI, art=albumArt, party=p, user=u)
                    s.save()
                
            else:
                searchResults = spotifyObject.search(search, 5, 0, "artist")
                artists = searchResults['artists']['items']

                for x in artists:
                    s = Searches(name = x['name'], uri = x['id'], party=p, user=u)
                    s.save()
                

            return HttpResponseRedirect(reverse('search_results', kwargs={'pid':pid}))
    else:

        form = searchForm(initial={'search':'',})
    context = {
        'form':form,
        'category':c,
        }
    
    return render(request, 'game/pickSong.html', context)

def searchResults(request, pid):
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
                    s = Songs(name=search.name,
                              uri=search.uri,
                              art=search.art,
                              user=u,
                              category=c,
                              played=False,
                              order=random.randint(1,101),
                              state = 'not_played',
                              )
                    s.save()
                    u.hasPicked = True
                    u.save()
                    Searches.objects.filter(user=u).filter(party=p).delete()
                    return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))

            elif ('back' in request.POST):
                Searches.objects.filter(user=u).filter(party=p).delete()
                return HttpResponseRedirect(reverse('pick_song', kwargs={'pid':pid}))

            elif('artist' in request.POST):
                spotifyObject = spotipy.Spotify(auth=p.token)
                search = form.cleaned_data['results']
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
        form = searchResultsForm(partyObject=p, userObject=u, initial={'results':''})
        
        
    context = {
               'form':form,
               'isArtist':isArtist,
               }
        
    return render(request, 'game/searchResults.html', context)

def getUser(request, p):
    
    sk = request.session.session_key
    current_user = Users.objects.filter(sessionID = sk, party = p)
    current_user = list(current_user)
    u = current_user[0]
    return u

def playMusic(pid):
    
    p = Party.objects.get(pk = pid)
    rN = p.roundNum
    print ('rN:', rN)
    spotifyObject = spotipy.Spotify(auth=p.token)
    while (Songs.objects.filter(category__party=p, category__roundNum = rN, state='not_played')):
       
        print ('playing music for round:', rN)
        queue = list(Songs.objects.filter(category__party=p, category__roundNum = rN, state='not_played'))
        for song in queue:
            ls = [song.uri]
            spotifyObject.start_playback(device_id=p.deviceID , uris=ls)
            song.state = 'playing'
            song.startTime = time.time()
            song.save()
            while(time.time() - song.startTime < 80):#p.time):
                continue
            song.state= 'played'
            song.save()

        rN = rN + 1
    print('EXITING THREAD')
