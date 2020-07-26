from django.shortcuts import render

def start(request):
    if not request.session.session_key:
        request.session.create()
    sk = request.session.session_key
       
    return render(request, 'start.html', {})

def index(request):
    if not request.session.session_key:
        request.session.create()
    sk = request.session.session_key
       
    return render(request, 'index.html', {})

def sandbox(request):

    return render(request, 'sandbox.html', {})

