from django.shortcuts import render
from utils.util_song import get_album_color
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User as Admin
from django.contrib.auth.decorators import user_passes_test
from party.forms import BlankForm
from spot.forms import FlyForm

from PIL import Image
from datetime import date, datetime
from .models import Fly, Play, Studio, Users
import requests
import shutil
import json
import spotipy
from os import remove
from os.path import exists
from utils.util_auth import create_token, check_token, get_url, generate_url
from queue_it_up.settings import IP, PORT, HEROKU, CLIENT_ID, CLIENT_SECRET, SPOT_URI, STATE
if STATE != 'DEV':
    from cairosvg import svg2png


fly_size = '16%'

@user_passes_test(lambda u: u.is_superuser)
def auth(request):
    url = get_url(str(request.get_full_path), HEROKU, IP, PORT)
    token_info = json.dumps(create_token(url=url, redirect_uri=SPOT_URI, scope=''))
    try:
        studio = Studio.objects.get(admin=request.user)
        studio.token_info = token_info
    except Exception as e:
        studio = Studio(
            admin=request.user,
            token_info = token_info
        )
    studio.save()
    return HttpResponseRedirect(
            reverse('studio', kwargs={'pid': 0})
    )  

@user_passes_test(lambda u: u.is_superuser)
def login(request):
    url = generate_url(
        scope='',
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=SPOT_URI
    )
    return HttpResponseRedirect(url)


def index(request):
    session_key = request.session.session_key
    if session_key is None:
        return HttpResponseRedirect(
            reverse('start')
        )           
    try:
        user = Users.objects.get(sessionID=session_key)
        fly = Fly.objects.filter(date=date.today()).first()
    except Exception as e:
        print("Could not locate User or Fly: " , e)
        return HttpResponseRedirect(
            reverse('start')
        )  
    play = Play.objects.filter(fly=fly, user=user).first()
    if play is None:
        return HttpResponseRedirect(
            reverse('start')
        )
    win = play.finish_time is not None
    started = play.start_time is not None
    context = {
        'song_title' : fly.album_name,
        'song_link' : fly.album_url,
        'artist_name' : fly.artist_name,
        'artwork' : fly.artwork_url,
        'background' : fly.image.url,
        'color' : fly.color,
        'x_mult': fly.x_mult,
        'y_mult': fly.y_mult,
        'play_x_mult': play.x_mult,
        'play_y_mult': play.y_mult,
        'play' : play.id,
        'user' : user.id,
        'win' : win,
        'started' : started,
        'time' : str(play.time),
        'start_time': str(play.start_time),
        'pathm' : play.pathm
    }
    return render(request, 'spot/index.html', context)


def start(request):
    if request.session.session_key is None:
        request.session.create()
    session_key = request.session.session_key
    try:
        user = Users.objects.get(sessionID = session_key)
    except Exception as e:
        print("Could not find a user with that session key, creating new user")
        user = Users(
            sessionID=session_key
        )
        user.save()
    
    fly = Fly.objects.filter(date=date.today()).first()
    play = Play.objects.filter(user=user.id, fly=fly.id).first()
    if(play):
        return HttpResponseRedirect(
            reverse('index', kwargs={})
        )
        
    if request.method == 'POST':
        form = BlankForm(request.POST)
        if form.is_valid():
            play = Play(
                user = user,
                fly = fly,
                pathm = []
            )
            play.save()
            return HttpResponseRedirect(
                reverse('index', kwargs={})
            )
    else:
        form = BlankForm(initial={'device': ''})
    context= {
        'form': form,
        'background' : fly.image.url,
    }
    return render(request, 'spot/start.html', context)


@user_passes_test(lambda u: u.is_superuser)
def studio(request, pid):
    try:
        fly = Fly.objects.get(id=pid)
    except Exception as e:
        if pid != 0:
            return HttpResponseRedirect(
                    reverse('studio', kwargs={'pid': 0})
            )
        else:
            fly = Fly(
                date = date.today()
            )
    if request.method == 'POST':
        form = FlyForm(request.POST)
        if form.is_valid():
            artwork = form.cleaned_data['artwork_url']
            x_coord = int(form.cleaned_data['x_coord'])
            y_coord = int(form.cleaned_data['y_coord'])
            fly_color = form.cleaned_data['color']
            fly.artwork_url = artwork
            fly.album_id = form.cleaned_data['result']
            fly.date=form.cleaned_data['date']
            file_name, x_mult, y_mult  = set_up(artwork, x_coord, y_coord, fly_color)
            fly.image = file_name
            fly.color = get_album_color(artwork)
            fly.fly_color = fly_color
            fly.x_coord = x_coord
            fly.y_coord = y_coord
            fly.x_mult = x_mult
            fly.y_mult = y_mult
            fly.album_name = form.cleaned_data['album_name']
            fly.artist_name = form.cleaned_data['artist_name']
            fly.album_url = form.cleaned_data['album_url']
            fly.save()
            return HttpResponseRedirect(
                reverse('studio', kwargs={'pid': fly.id})
            )
    else:
        form = FlyForm(initial={
            'artwork_url': fly.artwork_url,
            'album_name': fly.album_name,
            'artist_name': fly.artist_name,
            'album_url': fly.album_url,
            'x_coord': fly.x_coord,
            'y_coord': fly.y_coord,       
            'date': fly.date ,
            'color': fly.fly_color,
            'result': fly.album_id        
        })
    try:
        image = fly.image.url
    except Exception as e:
        image = ''

    context= {
        "form":form,
        "image":image,
        "artwork_url": fly.artwork_url,
        "fly_size": fly_size
    }
    return render(request, 'spot/studio.html', context)


def update_search(request):
    studio = Studio.objects.get(admin=request.user)
    result = request.GET.get('result', None)
    search_text = request.GET.get('text', None)
    token = json.loads(studio.token_info)['access_token']
    results = []
    try:
        spotify_object = spotipy.Spotify(auth=token)
        search_results = spotify_object.search(search_text, 15, 0, 'album')
        albums = search_results['albums']['items']
        for album in albums:
            results.append(
                {
                    'id':album['id'],
                    'name': album['name'],
                    'artist': album['artists'][0]['name'],
                    'uri' : album['uri'],
                    'image': album['images'][0]['url']
                }
            )
        status = 'success'
    except Exception as e:
        status = 'expired'
    data = {
        'albums': results,
        'status':status
    }

    return JsonResponse(data)


def update_play(request):
    stop = False
    pathm = []
    session_key = request.session.session_key
    user = Users.objects.get(sessionID=session_key)
    fly = Fly.objects.filter(date=date.today()).first()
    play = Play.objects.filter(user=user.id, fly=fly.id).first()
    if play and not play.finish_time:
        if not play.pathm:
            play.pathm = []
        play.pathm = play.pathm + json.loads(request.GET.get('pathm', None))
        if(len(play.pathm) > 0):
            play.x_mult = play.pathm[-1][0]
            play.y_mult = play.pathm[-1][1]
        play.save()
    else:
        stop = True

    data = {
        'stop': stop,
        'pathm': pathm
    }

    return JsonResponse(data)


def get_path(request):
    pathm = []  
    time = ''  
    session_key = request.session.session_key
    user = Users.objects.get(sessionID=session_key)
    fly = Fly.objects.filter(date=date.today()).first()
    play = Play.objects.filter(user=user.id, fly=fly.id).first()
    if play:
        if not play.pathm:
            play.pathm = []
        
        play.finish_time = request.GET.get('finish', None)
        play.x_mult = request.GET.get('x', None)
        play.y_mult = request.GET.get('y', None)
        play.save()
        play = Play.objects.filter(user=user.id, fly=fly.id).first()
        time = str(datetime.combine(date.today(), play.finish_time) - datetime.combine(date.today(), play.start_time))
        play.time = time
        play.pathm.append([play.x_mult, play.y_mult])
        play.save()
        pathm = play.pathm
    data = {
        'pathm': pathm,
        'time': time
    }
    return JsonResponse(data)


def set_start(request):
    try: 
        start_time = request.GET.get('start_time', None)
        if(start_time):
            session_key = request.session.session_key
            user = Users.objects.get(sessionID=session_key)
            fly = Fly.objects.filter(date=date.today()).first()
            play = Play.objects.get(user=user.id, fly=fly.id)
            play.start_time = start_time
            play.save()
            success = True
        else:
            success = False
    except Exception as e:
        success = False
    data = {
        'success': success
    }
    return JsonResponse(data)


def set_up(artwork_url, x_coord, y_coord, fly_color):
    if STATE != 'DEV':
        svg_code = '<svg xmlns="http://www.w3.org/2000/svg" height="8" width="10" viewBox="0 0 640 512"><!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path fill="{color}" d="M463.7 505.9c9.8-8.9 10.7-24.3 2.1-34.3l-42.1-49 0-54.7c0-5.5-1.8-10.8-5.1-15.1L352 266.3l0-.3L485.4 387.8C542.4 447.6 640 405.2 640 320.6c0-47.9-34-88.3-79.4-94.2l-153-23.9 40.8-40.9c7.8-7.8 9.4-20.1 3.9-29.8L428.5 90.1l38.2-50.9c8-10.6 6.1-25.9-4.3-34.1s-25.2-6.3-33.2 4.4l-48 63.9c-5.9 7.9-6.6 18.6-1.7 27.2L402.2 140 352 190.3l0-38.2c0-14.9-10.2-27.4-24-31l0-57.2c0-4.4-3.6-8-8-8s-8 3.6-8 8l0 57.2c-13.8 3.6-24 16.1-24 31l0 38.1L237.8 140l22.6-39.5c4.9-8.6 4.2-19.3-1.7-27.2l-48-63.9c-8-10.6-22.8-12.6-33.2-4.4s-12.2 23.5-4.3 34.1l38.2 50.9-23.9 41.7c-5.5 9.7-3.9 22 3.9 29.8l40.8 40.9-153 23.9C34 232.3 0 272.7 0 320.6c0 84.6 97.6 127 154.6 67.1L288 266l0 .3-66.5 86.4c-3.3 4.3-5.1 9.6-5.1 15.1l0 54.7-42.1 49c-8.6 10.1-7.7 25.5 2.1 34.3s24.7 7.9 33.4-2.1l48-55.9c3.8-4.4 5.9-10.2 5.9-16.1l0-55.4L288 344.7l0 63.1c0 17.7 14.3 32 32 32s32-14.3 32-32l0-63.1 24.3 31.6 0 55.4c0 5.9 2.1 11.7 5.9 16.1l48 55.9c8.6 10.1 23.6 11 33.4 2.1z"/></svg>'
        svg_code = svg_code.format(color=fly_color)
        svg2png(bytestring=svg_code,write_to='artwork/fly.png')    
    
    if artwork_url and len(artwork_url.split('image/')) > 1:
        art_id = artwork_url.split('image/')[1]
    response = requests.get(artwork_url, stream=True)
    img_id = 'artwork/img-'+ art_id +'.png' 
    with open(img_id, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    
    # Opening the primary image (used in background) 
    img1 = Image.open('artwork/img-'+ art_id +'.png' )
        
    # Opening the secondary image (overlay image) 
    img2 = Image.open('artwork/fly.png') 
    
    # Pasting img2 image on top of img1  
    # starting at coordinates (0, 0) 
    
    img1.paste(img2, (x_coord,y_coord), mask = img2)

    # Displaying the image 
    file_name = 'images/fly-img-' + art_id +'.png'
    img1.save('media/' + file_name)

    x_mult = x_coord / img1.width
    y_mult = y_coord / img1.height
    
    if exists(img_id):
        remove(img_id)
    return file_name, x_mult, y_mult