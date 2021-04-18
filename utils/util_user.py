from django.http import HttpResponseRedirect
from django.urls import reverse
from party.models import Party, Users, Songs

def get_user(request, party):
    ''' Returns the User object of the current user based on the Request
        and the Party. Will redirect user to homepage if user does not exist
        or if they are not a member of the party.

    Parameters:

        - request - web request
        - party - party object

    '''
    session_key = request.session.session_key
    try:
        current_user = Users.objects.get(
            sessionID=session_key, party=party, active=True
        )
    except Exception:
        return HttpResponseRedirect(reverse('index'))

    return current_user


def check_permission(pid, request):
    ''' Determines if user should have access to the page based on the isHost
        Permission

    Parameters:

        - request - web request
        - pid - pk of party object

    '''
    try:
        party = Party.objects.get(pk=pid, active=True)
    except Exception:
        return False
    session_key = request.session.session_key
    try:
        user = Users.objects.get(sessionID=session_key, party=party)
    except Exception:
        print('here')
        return False
    if not user.isHost:
        return False
    else:
        return True


def like_song(song, user, request):
    ''' Increments or Decrements the like field of a Song object based on the
        request. Prevents user from liking one song multiple times.

    Parameters:

        - request - web request
        - song - song object
        - user - user object

    '''
    if song and not song.duplicate:
        if 'like' in request.POST:
            song.likes += 1
        else:
            song.likes -= 1
        song.save()
        user.hasLiked = True
        user.save()


def assign_leader(party):
    ''' Selects a random user from the party to be the leader to select the next
        category. Prevents a user from having to pick in back to back rounds.

    Parameters:

        - party - party object

    '''
    leader = Users.objects.filter(
        turn='not_picked',
        party=party,
        active=True
    ).order_by('?').first()
    if not leader:
        picked_last = -1
        users = Users.objects.filter(party=party, active=True).all()
        for user in users:
            if user.turn == 'has_picked_last':
                picked_last = user.id
            user.turn = 'not_picked'
            user.save()
        leader = Users.objects.filter(
            party=party,
            active=True
        ).exclude(pk=picked_last).order_by('?').first()
        if not leader:
            leader = Users.objects.filter(
                party=party,
                active=True
            ).order_by('?').first()
    leader.turn = 'picking'
    leader.save()


def reset_users(party):
    ''' Sets the hasPicked [song] field of all active users in a party to false 

    Parameters:

        - party - party object

    '''
    users = Users.objects.filter(party=party, active=True).all()
    for user in users:
        user.hasPicked = False
        user.save()


def set_user_points(party, round_number):
    ''' Adds Each Songs Likes to the User's Total Likes 

    Parameters:

        - party - party object
        - round_number - the number of the current round

    '''
    songs = Songs.objects.filter(category__party=party, category__roundNum=round_number)
    for song in songs:
        user = song.user
        user.points = user.points + song.likes
        user.save()


def reset_user_likes(party):
    ''' Resets each Active User to not having liked

    Parameters:

        - party - party object

    '''
    users = Users.objects.filter(party=party, active=True)
    for user in users:
        user.hasLiked = False
        user.save()


def get_like_threshold(party):
    ''' Returns an integer of the number of down votes needed to skip a song

    Parameters:

        - party - party object

    '''
    users = Users.objects.filter(party=party, active=True).all()
    threshold = len(list(users)) * (-1) + 1
    if threshold == 0:
        threshold = -1
    
    return threshold