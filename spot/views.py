from django.shortcuts import render
from utils.util_song import get_album_color
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User as Admin
from django.contrib.auth.decorators import user_passes_test
from party.forms import BlankForm
from spot.forms import FlyForm, DayForm
from PIL import Image
from datetime import date, datetime, timedelta, timezone
from .models import Day, Fly, Play, Studio, Users
import requests
import shutil
import json
import spotipy
import boto3
from os import remove
from os.path import exists
from utils.util_auth import create_token, check_token, get_url, generate_url
from queue_it_up.settings import (
    IP, PORT, HEROKU, CLIENT_ID, CLIENT_SECRET, SPOT_URI, STATE,
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME,
    AWS_S3_CUSTOM_DOMAIN
)
if STATE != 'DEV':
    from cairosvg import svg2png


fly_size = '16%'


def index(request):
    tzinfo = get_tz_info()
    session_key = request.session.session_key
    if session_key is None:
        return HttpResponseRedirect(
            reverse('start')
        )           
    try:
        user = Users.objects.get(sessionID=session_key)
        day = Day.objects.get(date=datetime.now(tzinfo).date())
        fly = Fly.objects.get(id=day.fly.id)
        if not fly.image_url:
            raise Exception()
    except Exception as e:
        print("Could not locate User, Day, or Fly: " , e)
        return HttpResponseRedirect(
            reverse('start')
        )  
    play = Play.objects.filter(day=day, user=user).first()
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
        'background' : fly.image_url,
        'color' : fly.color,
        'x_mult': fly.x_mult,
        'y_mult': fly.y_mult,
        'play_x_mult': play.x_mult,
        'play_y_mult': play.y_mult,
        'play' : play.id,
        'user' : user.id,
        'win' : win,
        'started' : started,
        'give_up' : play.give_up,
        'time' : str(play.time),
        'start_time': str(play.start_time),
        'pathm' : play.pathm
    }
    return render(request, 'spot/index.html', context)


def start(request):
    tzinfo = get_tz_info()
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
    try:
        day = Day.objects.get(date=datetime.now(tzinfo).date())
        fly = Fly.objects.get(id=day.fly.id)
        if not fly.image_url:
            raise Exception()
    except Exception as e:
        return HttpResponseRedirect(
            reverse('sorry')
        )
    play = Play.objects.filter(user=user.id, day=day.id).first()
    if(play):
        return HttpResponseRedirect(
            reverse('index', kwargs={})
        )
        
    if request.method == 'POST':
        form = BlankForm(request.POST)
        if form.is_valid():
            play = Play(
                user = user,
                day = day,
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
        'background' : fly.image_url,
    }
    return render(request, 'spot/start.html', context)


def sorry(request):
    tzinfo = get_tz_info()
    try:
        day = Day.objects.get(date=datetime.now(tzinfo).date())
        fly = Fly.objects.get(id=day.fly.id)
        if not fly.image_url:
            raise Exception()
        return HttpResponseRedirect(
            reverse('start')
        ) 
    except Exception as e:
        pass
        
    context= {
    }
    return render(request, 'spot/sorry.html', context)



@user_passes_test(lambda u: u.is_superuser)
def admin(request):
    context = {
    }
    return render(request, 'spot/admin.html', context)

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


@user_passes_test(lambda u: u.is_superuser)
def calendar(request, date_param='default'):
    tzinfo = get_tz_info()
    if date_param == 'default':
        date_param = str(datetime.now(tzinfo).date())
    context = {
        'date' : date_param
    }
    return render(request, 'spot/calendar.html', context)


@user_passes_test(lambda u: u.is_superuser)
def stats(request, date_param='default'):
    tzinfo = get_tz_info()
    if date_param == 'default':
        date_param = str(datetime.now(tzinfo).date())
    day_date = datetime.strptime(date_param, "%Y-%m-%d").date()
    try:
        day = Day.objects.get(date=day_date)
    except Exception as e:
        day = Day(date=day_date)
    users_total = len(Users.objects.all())
    plays_total = len(Play.objects.all())
    users_today = len(Users.objects.filter(created__gte=day_date).all())
    plays_today = len(Play.objects.filter(day=day.id).all())
    users_return = len(Users.objects.filter(created__lte=day_date, last_visited__gte=day_date).all())
    context = {
        'users_total' : users_total,
        'plays_total' : plays_total,
        'users_today' : users_today,
        'plays_today' : plays_today,
        'users_return' : users_return
    }
    return render(request, 'spot/stats.html', context)


@user_passes_test(lambda u: u.is_superuser)
def day(request, date_param):
    day_date = datetime.strptime(date_param, "%Y-%m-%d").date()
    try:
        day = Day.objects.get(date=day_date)
    except Exception as e:
        day = Day(date=day_date)

    if request.method == 'POST':
        form = DayForm(request.POST)
        if form.is_valid():
            fly_id = form.cleaned_data['result']
            fly = Fly.objects.get(id=fly_id)
            day.fly = fly         
            day.date = day_date
            day.save()
            return HttpResponseRedirect(
                reverse('calendar', kwargs={'date_param': day_date})
        )
    else:
        form = DayForm(initial={
            'result': day.fly,     
        })
        if day.fly:
            fly = Fly.objects.filter(id=day.fly.id).first()
        else:
            fly = None
        if fly:
            artwork_url = fly.artwork_url
        else:
            artwork_url = 'https://www.svgrepo.com/show/508699/landscape-placeholder.svg'
    context = {
        'form': form,
        'day' : day,
        'fly' : fly,
        'artwork_url': artwork_url
    }
    return render(request, 'spot/day.html', context)


def get_dates(request):
    days = []
    start = request.GET.get('start', None)
    find_date = datetime.strptime(start, "%Y-%m-%d").date()
    for i in range(1,8):
        obj = {
           'date': str(find_date),
           'image': 'https://www.svgrepo.com/show/508699/landscape-placeholder.svg',
           'name': 'Nothing here yet...',
           'artist': '', 
           'id': '0'
        }
        day = Day.objects.filter(date=find_date).first()
        if(day):
            fly = Fly.objects.get(id=day.fly.id)
            obj['id'] = day.id
            obj['image']  = fly.artwork_url
            obj['name'] = fly.album_name
            obj['artist'] = fly.artist_name
        days.append(obj)
        find_date = find_date + timedelta(days=1)
    
    data = {
       'days':days
    }
    return JsonResponse(data)


def get_flys(request):
    f = []
    search_text = request.GET.get('text', None)
    if search_text != '':
        flys = Fly.objects.filter(album_name__icontains = search_text).all()
    else:
        flys = Fly.objects.all()
    count = 0
    for fly in flys:
        if count > 10:
            break
        f.append(
            {
                'id': fly.id,
                'image': fly.artwork_url,
                'name' : fly.album_name,
                'artist': fly.artist_name
            }
        )
        count = count + 1    
    data = {
        'flys' : f
    }
    return JsonResponse(data)


def update_search(request):
    studio = Studio.objects.get(admin=request.user)
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
    tzinfo = get_tz_info()
    stop = False
    pathm = []
    session_key = request.session.session_key
    user = Users.objects.get(sessionID=session_key)
    day = Day.objects.get(date=datetime.now(tzinfo).date())
    play = Play.objects.get(user=user.id, day=day.id)
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
    tzinfo = get_tz_info()
    pathm = []  
    time = ''  
    session_key = request.session.session_key
    user = Users.objects.get(sessionID=session_key)
    day = Day.objects.get(date=datetime.now(tzinfo).date())
    play = Play.objects.get(user=user.id, day=day.id)
    if play:
        if not play.pathm:
            play.pathm = []
        
        play.finish_time = request.GET.get('finish', None)
        play.x_mult = request.GET.get('x', None)
        play.y_mult = request.GET.get('y', None)
        play.give_up = request.GET.get('give_up', None) == "true"
        play.save()
        play = Play.objects.get(user=user.id, day=day.id)
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
    tzinfo = get_tz_info()
    try: 
        start_time = request.GET.get('start_time', None)
        if(start_time):
            session_key = request.session.session_key
            user = Users.objects.get(sessionID=session_key)
            day = Day.objects.get(date=datetime.now(tzinfo).date())
            play = Play.objects.get(user=user.id, day=day.id)
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


def update_give_up(request):
    try:
        tzinfo = get_tz_info()
        session_key = request.session.session_key
        user = Users.objects.get(sessionID=session_key)
        day = Day.objects.get(date=datetime.now(tzinfo).date())
        play = Play.objects.get(user=user.id, day=day.id)
        play.give_up = True
        play.save()
        success = True
    except Exception as e:
        success = False
    data = {
        'success': success
    }
    return JsonResponse(data)

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
            fly = Fly()
    if request.method == 'POST':
        form = FlyForm(request.POST)
        if form.is_valid():
            artwork = form.cleaned_data['artwork_url']
            width = float(form.cleaned_data['width'])
            x_mult = int(form.cleaned_data['x_coord']) / width
            y_mult = int(form.cleaned_data['y_coord']) / width
            fly.x_mult = x_mult
            fly.y_mult = y_mult
            fly.width = width
            fly_color = form.cleaned_data['color']
            fly.artwork_url = artwork
            fly.album_id = form.cleaned_data['result']
            file_name = set_up(artwork, x_mult, y_mult, fly_color)
            fly.image_url = AWS_S3_CUSTOM_DOMAIN + '/' + file_name
            fly.color = get_album_color(artwork)
            fly.fly_color = fly_color
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
            'x_coord': fly.x_mult * fly.width,
            'y_coord': fly.y_mult * fly.width,
            'color': fly.fly_color,
            'result': fly.album_id,
            'width' : fly.width     
        })
    try:
        image = fly.image_url
    except Exception as e:
        image = ''
    preview = fly.image_url != None
    context= {
        "fly":fly,
        "form":form,
        "image":image,
        "artwork_url": fly.artwork_url,
        "fly_size": fly_size,
        "preview" : preview
    }
    return render(request, 'spot/studio.html', context)


def set_up(artwork_url, x_mult, y_mult, fly_color):
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
    if img1.mode == "CMYK":
        img1 = img1.convert("RGB")
        
    # Opening the secondary image (overlay image) 
    img2 = Image.open('artwork/fly.png')
    
    # Pasting img2 image on top of img1  
    # starting at coordinates (0, 0) 
    x_coord = int(x_mult * img1.width)
    y_coord = int(y_mult * img1.height)    
    img1.paste(img2, (x_coord,y_coord), mask = img2)

    # Displaying the image 
    file_name = 'media/images/fly-img-' + art_id +'.png'    
    img1.save(file_name)
    s3_key = STATE + '/images/'  + 'fly-img-' + art_id
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3.upload_file(file_name, AWS_STORAGE_BUCKET_NAME,  s3_key, ExtraArgs={'ContentType': 'image/png'})
    
    if exists(img_id):
        remove(img_id)

    if exists(file_name):
        remove(file_name)

    return s3_key


def get_tz_info():
    timezone_offset = -9.0 
    tzinfo = timezone(timedelta(hours=timezone_offset))
    return tzinfo