from django.urls import path
from start import views

urlpatterns = [
    path('', views.start, name='start'),
    path('index', views.index, name='index'),
    path('sandbox', views.sandbox, name='sandbox'),
]