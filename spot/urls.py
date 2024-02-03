from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("start", views.start, name="start"),
    path("studio", views.studio, name="studio"),
    path('update_play', views.update_play, name='update_play'),
    path('get_path', views.get_path, name="get_path"),
    path('set_start', views.set_start, name="set_start")
]