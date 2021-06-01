from party.models import Party, Users, Songs, Library, Category
from datetime import datetime, timedelta, timezone
from queue_it_up.settings import SYSTEM
from django.http import HttpResponseRedirect
from django.urls import reverse
from utils.util_rand import get_numbers, get_letter
from utils.util_user import get_like_threshold, get_like_total
import time


def get_party(pid):
    try:
        return Party.objects.get(pk=pid, active=True)
    except Exception:
        return -1


def get_inactivity(pid, duration):
    p = Party.objects.get(pk=pid)
    now = datetime.now(timezone.utc)
    inactivity = ((now - p.last_updated).seconds // 60) % 60
    return inactivity > duration


def clean_up_party(pid):
    p = Party.objects.get(pk=pid)
    p.active=False
    p.token = ""
    p.token_info = ""
    p.url = ""
    p.url_open = ""
    p.deviceID = ""
    p.save()


def set_lib_repo():
    lib_set = set()
    libraries = Library.objects.filter(visible=True).exclude(special=True)
    for library in libraries:
        lib_set.add(library.id)
    return lib_set


def get_results(party):
    results=[]
    if party.roundNum > 1:
        song_results = Songs.objects.filter(
            category__roundNum = party.roundNum - 1, category__party=party
            ).order_by('-likes').all()
        for result in song_results:
            art = result.art
            if art == "duplicate":
                duplicate = Songs.objects.filter(
                    category__roundNum = party.roundNum - 1, 
                    category__party=party, 
                    name=result.name).exclude(art="duplicate").first()
                art = duplicate.art
            results.append(
                {
                    "user_result":result.user.name,
                    "song_result":result.name,
                    "like_result":result.likes,
                    "total_result":result.user.points,
                    "art_result":art,
                    "category_result":result.category.name
                }
            )
    else:
        results.append({"category_result": "No Results Yet" })
    return results


def get_totals(party):
    totals=[]
    if party.roundNum > 1:
        users = Users.objects.filter(
            party=party, active=True).order_by('-points').all()
        for user in users:
            totals.append(
                {
                    "user_total":user.name,
                    "points_total":user.points
                }
            )
    return totals


def get_category_choices(request, party):
    if request.method != 'POST' and party.indices is None:
        num = 12
        if len(party.lib_repo) < num:
            num = len(party.lib_repo)
        party.indices = get_numbers(num, len(party.lib_repo))
        party.save() 
    repo = set()
    list_repo = list(party.lib_repo)
    for i in party.indices:
        repo.add(list_repo[int(i)])
    return repo


def create_category(party, user, category, artist, custom, sc_type):
    valid = True
    if not category:
        return not valid

    choice = category.display
    
    if choice == 'Songs by this Artist':
        if artist != '':
            name ='Songs by ' + artist
        else:
            return not valid
    elif choice == 'Custom': 
        if custom != '':
            name = custom
            library = Library.objects.filter(name=custom).all()
            if not library:
                Library(name=custom).save()
        else:
            return not valid
    elif choice == 'Scattergories':
        name =  sc_type + ' Names that Begin with the Letter ' + get_letter()
    else:
        name = choice
    
    if not category.special:
        party.lib_repo.remove(str(category.pk))
    party.indices = None  
    party.save()
    
    Category(
        name = name,
        roundNum = party.roundTotal + 1,
        party = party,
        leader = user,
        library = category
    ).save()

    return valid


def check_duplicate(party, round_number, song):
    dups = list(Songs.objects.filter(
                    category__party=party,
                    category__roundNum=round_number,
                    state='not_played',
                    name=song.name
            ).all())
    if len(dups) > 1:
        for d in dups:
            d.duplicate=True
            d.save()
            u = d.user
            u.hasLiked=True
            u.save()
        song.duplicate=True
        song.save()


def get_song_length(song):
    duration = song.duration / 1000
    party = song.category.party
    if duration < party.time or (song.duplicate and duration < 180):
        length = duration - 5
    elif song.duplicate:
        length = 180 
    else:
        length = party.time
    return length


def wait_for_song(song):
    party = song.category.party
    song_length = get_song_length(song)
    threshold = get_like_threshold(party)
    flag = True
    while(time.time() - song.startTime < song_length): 
        if get_like_total(song) <= threshold:
            break
        if song.duplicate and (time.time() - song.startTime) >= party.time and flag:
            song.art= "duplicate"
            song.save()
            flag = False