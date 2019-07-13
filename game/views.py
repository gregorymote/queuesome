from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from party.models import Party
from party.models import Users
from game.forms import blankForm


def lobby(request, pid):

    a = Party.objects.get(pk = pid)
    print(a.started)  

    if request.method == 'POST':
        form = blankForm(request.POST)

        if form.is_valid():
            
            return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    else:
        form = blankForm(initial={'text':'blank',})
        a = Party.objects.get(pk = pid)
        print(a.started)  
        if a.started:
            return HttpResponseRedirect(reverse('play', kwargs={'pid': pid}))

    guests = Users.objects.filter(party = pid)
    guests = list(guests)


    sk = request.session.session_key

    current_user = Users.objects.filter(sessionID = sk, party = pid, isHost = True)
    current_user = list(current_user)
    if len(current_user) == 0:
        access =  False
    else:
        access = True
    
    party_name = guests[0].party.name
    context = {
        'guests':guests,
        'party_name': party_name,
        'access': access,
        'form': form,
        }

    
    return render(request, 'game/lobby.html', context)

def play(request, pid):
    a = Party.objects.get(pk = pid)
    if not a.started:
        a.started = True
        a.save()  

    return render(request, 'game/play.html')

    
