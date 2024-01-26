from django.shortcuts import render
from utils.util_song import get_album_color
#from cairosvg import svg2png
from PIL import Image
import requests
import shutil

def set_up(image_url, x_coord, y_coord):
    #svg_code = '<svg xmlns="http://www.w3.org/2000/svg" height="8" width="10" viewBox="0 0 640 512"><!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path fill="#FFFFF" d="M463.7 505.9c9.8-8.9 10.7-24.3 2.1-34.3l-42.1-49 0-54.7c0-5.5-1.8-10.8-5.1-15.1L352 266.3l0-.3L485.4 387.8C542.4 447.6 640 405.2 640 320.6c0-47.9-34-88.3-79.4-94.2l-153-23.9 40.8-40.9c7.8-7.8 9.4-20.1 3.9-29.8L428.5 90.1l38.2-50.9c8-10.6 6.1-25.9-4.3-34.1s-25.2-6.3-33.2 4.4l-48 63.9c-5.9 7.9-6.6 18.6-1.7 27.2L402.2 140 352 190.3l0-38.2c0-14.9-10.2-27.4-24-31l0-57.2c0-4.4-3.6-8-8-8s-8 3.6-8 8l0 57.2c-13.8 3.6-24 16.1-24 31l0 38.1L237.8 140l22.6-39.5c4.9-8.6 4.2-19.3-1.7-27.2l-48-63.9c-8-10.6-22.8-12.6-33.2-4.4s-12.2 23.5-4.3 34.1l38.2 50.9-23.9 41.7c-5.5 9.7-3.9 22 3.9 29.8l40.8 40.9-153 23.9C34 232.3 0 272.7 0 320.6c0 84.6 97.6 127 154.6 67.1L288 266l0 .3-66.5 86.4c-3.3 4.3-5.1 9.6-5.1 15.1l0 54.7-42.1 49c-8.6 10.1-7.7 25.5 2.1 34.3s24.7 7.9 33.4-2.1l48-55.9c3.8-4.4 5.9-10.2 5.9-16.1l0-55.4L288 344.7l0 63.1c0 17.7 14.3 32 32 32s32-14.3 32-32l0-63.1 24.3 31.6 0 55.4c0 5.9 2.1 11.7 5.9 16.1l48 55.9c8.6 10.1 23.6 11 33.4 2.1z"/></svg>'
    #svg2png(bytestring=svg_code,write_to='static/fly.png')    
    
    if image_url and len(image_url.split('image/')) > 1:
        art_id = image_url.split('image/')[1]
    response = requests.get(image_url, stream=True)
    img_id = 'artwork/img-'+ art_id+ '-' +'.png' 
    with open(img_id, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    
    # Opening the primary image (used in background) 
    img1 = Image.open('artwork/img-'+ art_id+ '-' +'.png' )
        
    # Opening the secondary image (overlay image) 
    img2 = Image.open('static/images/fly.png') 
    
    # Pasting img2 image on top of img1  
    # starting at coordinates (0, 0) 
    
    img1.paste(img2, (x_coord,y_coord), mask = img2)

    # Displaying the image 
    file_name = 'static/fly-img-' + art_id +'.png'
    img1.save(file_name)

    x_mult = x_coord / img1.width
    y_mult = y_coord / img1.height
    
    return 'fly-img-' + art_id +'.png', x_mult, y_mult


def index(request):
    artwork = 'https://i.scdn.co/image/ab67616d0000b2730c3a1b46b6b846dfdfbc6a7d'
    x_coord = 210
    y_coord = 350
    file_name, x_mult, y_mult  = set_up(artwork, x_coord, y_coord)
    #color = get_album_color(artwork)
    context = {
        'song_title' : "This is the title of the song a long lon long song title",
        'song_link' : '/',
        'artist_name' : 'This is the artist',
        'artwork' : artwork,
        'background' : file_name,
        'color' : '130, 128, 131',
        'x_mult': x_mult,
        'y_mult': y_mult,
    }
    return render(request, 'spot/index.html', context)