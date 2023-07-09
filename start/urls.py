from django.urls import path
from start import views

urlpatterns = [
    path('', views.start, name='start'),
    path('index', views.index, name='index'),
    path('about', views.about, name='about'),
    path('tutorial', views.tutorial, name='tutorial'),
]