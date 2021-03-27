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
        p = Party.objects.get(pk=pid, active=True)
    except Exception:
        return False
    session_key = request.session.session_key
    try:
        u = Users.objects.get(sessionID=session_key, party = p)
    except Exception:
        return False
    if not u.isHost:
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