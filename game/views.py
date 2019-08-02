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
import random
import os

def lobby(request, pid):

    p = Party.objects.get(pk = pid)
    
    if request.method == 'POST':
        form = blankForm(request.POST)

        if form.is_valid():
            
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
                u.turn = 'not_picked'
                u.save()
            x = list(users)
            lead = x[0]
            lead.turn = 'picking'
            lead.save()
            p.state = 'choose_category'
            p.save()
        
        c = Category(name = lead.name + " is Picking the Category",
                     roundNum = p.roundTotal,
                     party = p,
                     leader = lead,
                    )
        c.save()

        if not p.started:
            p.started = True
            p.save()


    if len(list(Users.objects.filter(party=p, hasPicked=False))) == 0 and p.state == 'pick_song':
        p.roundTotal = p.roundTotal + 1
        p.state = 'assign'
        p.save()
        
        users = Users.objects.filter(party = p)
        for x in users:
            x.hasPicked = False
            x.save()

        #os.system('python party/playMusic.py %s' % (pid))
        
    c = Category.objects.get(party=p, roundNum=p.roundNum)  
        
    if request.method == 'POST':
        form = blankForm(request.POST)

        if form.is_valid():
            if p.state == 'choose_category':
                return HttpResponseRedirect(reverse('choose_category', kwargs={'pid':pid}))
            if p.state == 'pick_song':
                return HttpResponseRedirect(reverse('pick_song', kwargs={'pid':pid}))
    else:
        form = blankForm(initial={'text':'blank',})

    context = {
        'form':form,
        'party': p,
        'user' : u,
        'category' : c, 
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
    isArtist = (list(Searches.objects.filter(party=p).filter(user=u))[0].art == None)

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
                              order=random.randint(1,101)
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
    #print(sk)
    current_user = Users.objects.filter(sessionID = sk, party = p)
    current_user = list(current_user)
    u = current_user[0]
    return u
    
