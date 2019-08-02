import sys
import spotipy
from models import Party
from models import Users
from models import Category
from models import Songs
from models import Searches

def play(pid):
    p = Party.objects.get(pk = pid)
    spotifyObject = spotipy.Spotify(auth=p.token)

    queue = Songs.objects.filter(categoroy__party=p, category__roundNum = p.roundNum)

    for x in queue:
        print (x['name'])

    p.roundNum = p.roundNum + 1
    p.save()

if __name__ == "__main__":
    partyID = int(sys.argv[1])
    play(partyID)
