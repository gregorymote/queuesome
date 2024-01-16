from django.shortcuts import render
from utils.util_song import get_album_color

# Create your views here.
def index(request):
    artwork = 'https://i.scdn.co/image/ab67616d0000b2730c3a1b46b6b846dfdfbc6a7d'
    #print(get_album_color(artwork))
    context = {
        'song_title' : "This is the title of the song a long lon long song title",
        'song_link' : '/',
        'artist_name' : 'This is the artist',
        'artwork' : artwork,
        'color' : '130, 128, 131'
    }
    return render(request, 'spot/index.html', context)