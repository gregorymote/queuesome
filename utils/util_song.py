from utils.spotify_background_color import SpotifyBackgroundColor
from party.models import Songs
from PIL import Image
from numpy import asarray
import os
from os import remove
from os.path import exists
import requests
import shutil
from queue_it_up.settings import QDEBUG


def get_bg_color(song_id):
    color = '130, 128, 131'
    song = Songs.objects.get(id=song_id)
    if song and len(song.art.split('image/')) > 1:
        art_id = song.art.split('image/')[1]
    else:
        art_id = None
    if art_id:
        response = requests.get(song.art, stream=True)
        img_id = 'artwork/img-'+ str(song_id) + '-' + art_id +'.png'
        print(QDEBUG,img_id)
        try:
            with open(img_id, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            image = Image.open(img_id)
            numpydata = asarray(image)
            if exists(img_id):
                remove(img_id)
            try:
                SBC = SpotifyBackgroundColor(img=numpydata)
                colors = SBC.best_color()
                intensity = (colors[0]*0.299 + colors[1]*0.587 + colors[2]*0.114)
                if intensity < 186:
                    color = str(round(colors[0])) +', '+ str(round(colors[1])) +', '+ str(round(colors[2]))
            except Exception:
                print(QDEBUG,'Unable to Find Background color for ' + song.name)
            song = Songs.objects.get(id=song_id)
            song.color = color
            song.save()
        except Exception as e:
            print(QDEBUG,e)
        finally:
            if exists(img_id):
                remove(img_id)