from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from party.models import Party
from party.models import Users
from party.models import Category
from game.forms import blankForm
from game.forms import chooseCategoryForm


def lobby(request, pid):

    p = Party.objects.get(pk = pid)
    
    if request.method == 'POST':
        form = blankForm(request.POST)

        if form.is_valid():
            
            return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    else:
        form = blankForm(initial={'text':'blank',})
        p = Party.objects.get(pk = pid)
          
        if p.started:
            return HttpResponseRedirect(reverse('play', kwargs={'pid': pid}))

    guests = Users.objects.filter(party = pid)
    guests = list(guests)

    u = getUser(request, pid)
    
    if u.isHost:
        access =  True
    else:
        access = False
    
    party_name = guests[0].party.name
    context = {
        'guests':guests,
        'party_name': party_name,
        'access': access,
        'form': form,
        }

    
    return render(request, 'game/lobby.html', context)



def play(request, pid):

    p = Party.objects.get(pk = pid)
    u = getUser(request, pid)

    if p.state == 'assign':
        x = list(Users.objects.filter(party=p, turn='not_picked'))
        lead = x[0]
        lead.turn = 'picking'
        lead.save()
        p.state = 'choose_category'
        p.save()
        
        c = Category(name = lead.name + " is Picking the Category",
                     roundNum = p.roundTotal,
                     party = p,
                     leader = lead,
                    )
        c.save()

        if not p.started:
            p.started = True
            p.save()

                
    c = Category.objects.get(party=p, roundNum=p.roundNum)  
        
    if request.method == 'POST':
        form = blankForm(request.POST)

        if form.is_valid():
            if p.state == 'choose_category':
                return HttpResponseRedirect(reverse('choose_category', kwargs={'pid':pid}))
            
    else:
        form = blankForm(initial={'text':'blank',})

    context = {
        'form':form,
        'party': p,
        'user' : u,
        'category' : c, 
        }
    
    return render(request, 'game/play.html', context)



def chooseCat(request, pid):
    default = ''
    p = Party.objects.get(pk=pid)
    showCustom = False
    
    if request.method == 'POST':
        form = chooseCategoryForm(request.POST)

        if form.is_valid():

            if form.cleaned_data['cat_choice'].name != 'custom': 
                createCategory(form.cleaned_data['cat_choice'].name, request, p)

                return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
            else:
                showCustom = True

                if form.cleaned_data['custom'] != default:
                    createCategory(form.cleaned_data['custom'], request, p)
                    return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    else:

        form = chooseCategoryForm(initial={
                                           'cat_choice':'',
                                           'custom':default,
                                           }
                                  )
    context = {
        'form':form,
        'showCustom':showCustom,
        }
    #print(showCustom)
    return render(request, 'game/chooseCat.html', context)


def createCategory(choice, request, p):

    u = getUser(request, p)
    u.turn = 'has_picked'
    u.save()

    c = Category.objects.get(party=p, roundNum=p.roundTotal)
    c.name = choice
    c.save()

    p.roundTotal = p.roundTotal + 1
    p.state = 'pick_song'
    p.save()



def getUser(request, p):
    
    sk = request.session.session_key
    #print(sk)
    current_user = Users.objects.filter(sessionID = sk, party = p)
    current_user = list(current_user)
    u = current_user[0]
    return u
    
