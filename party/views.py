from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from party.forms import NamePartyForm
from party.forms import CreateUserForm
from party.models import Party
from party.models import Users

def name_party(request):

    if request.method == 'POST':

        form = NamePartyForm(request.POST)

        if form.is_valid():
            p = Party(name=form.cleaned_data['party_name'],
                      category = "",
                      started = False,
                      
                      )
            p.save()          
            
            u = Users(
                name = form.cleaned_data['user_name'],
                party = p,
                sessionID = request.session.session_key,
                points = 0,
                isHost = True,
                hasSkip = True,
                state = "",
                turn = "",
                )
            u.save()
                
            return HttpResponseRedirect(reverse('lobby', kwargs={'pid':p.pk}))
        
    else:

            
        form = NamePartyForm(initial={
                                    'party_name' : 'Enter a Party Name',
                                    'user_name' : 'name'})


    context = {
        'form' : form,
        }

    return render(request, 'party/name_party.html', context)

def create_user(request):

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():

            #print('\n\n\n\n',request.session.session_key,'\n\n\n\n\n')
            u = Users(
                    name= form.cleaned_data['user_name'],
                    party = form.cleaned_data['party_choice'],
                    sessionID = request.session.session_key,
                    points = 0,
                    isHost = False,
                    hasSkip = True,
                    state = "",
                    turn = "",
                    )
            u.save()

            

            return HttpResponseRedirect(reverse('lobby', kwargs={'pid':u.party.pk}))
    else:
        form = CreateUserForm(initial={
                                        'party_choice': '',
                                        'user_name': 'name'})

    context = {
        'form' : form,
        }

    return render(request, 'party/create_user.html', context)
