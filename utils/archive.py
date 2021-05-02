def search_results(request, pid):

    p = get_party(pid)
    u = get_user(request, p)
    invalid = False
    
    if u.hasPicked:
        return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
    
    c = Category.objects.filter(party=p, roundNum=p.roundTotal).first() 
    try:
        isArtist = (list(Searches.objects.filter(party=p).filter(user=u))[0].art == None)
    except Exception:
        isArtist = True
        
    if request.method == 'POST':
        form = searchResultsForm(request.POST, partyObject=p, userObject=u)
        if form.is_valid():
            if ('add2q' in request.POST):
                search = form.cleaned_data['results']
                if search != None:
                    s = Songs(
                              name=search.name,
                              uri=search.uri,
                              art=search.art,
                              user=u,
                              category=c,
                              played=False,
                              order=random.randint(1,101),
                              state='not_played',
                              link=search.link,
                              duration=search.duration,
                    )
                    s.save()
                    u.hasPicked = True
                    u.save()
                    Searches.objects.filter(user=u, party=p).delete()

                    not_picked = Users.objects.filter(party=p, active=True, hasPicked=False)
                    if not not_picked:
                        c.full = True
                        c.save()

                    return HttpResponseRedirect(reverse('play', kwargs={'pid':pid}))
                else:
                    invalid = True

            elif ('back' in request.POST):
                Searches.objects.filter(user=u).filter(party=p).delete()
                return HttpResponseRedirect(reverse('pick_song', kwargs={'pid':pid}))
    else:
        form = searchResultsForm(partyObject=p, userObject=u, initial={'results':''})
   
    album_search = list(Searches.objects.filter(party=p, user=u).order_by('pk'))
        
    context = {
               'form':form,
               'isArtist':isArtist,
               'invalid':invalid,
               'albumSearch':album_search
               }
        
    return render(request, 'game/search_results.html', context)


    #TBD OBE
def update_game(request):
    ''' Ajax request made by system to update the game logic 

    Parameters:

        - request - web request

    '''
    pid = request.GET.get('pid', None)   
    party = Party.objects.get(pk=pid)

    if get_inactivity(pid,20):
        clean_up_party(party.pk)

    if party.state == 'assign' or \
            (party.state =='choose_category' and not 
                Users.objects.filter(
                    turn='picking',
                    party=party,
                    active=True
                ).first()
            ):
        assign_leader(party)
        party.state = 'choose_category'
        party.save()  
                
    if party.state == 'pick_song' and not \
            Users.objects.filter(
                hasPicked=False,
                party=party,
                active=True
            ).all():
        reset_users(party) 
        party.state = 'assign'
        party.save()
    if not party.device_error:
        if not party.thread and \
                Songs.objects.filter(
                    category__party=party,
                    category__roundNum=party.roundNum,
                    state='not_played',
                    category__full=True
                ):
            thread = threading.Thread(target=play_songs, args=(pid,))
            thread.start()
    else:
        party.device_error = activate_device(
            token_info=party.token_info,
            party_id=party.pk,
        )
        party.save()
    data={
        "success": 'True',
        "inactive" : not party.active
    }

    return JsonResponse(data)