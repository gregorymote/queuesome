from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("start", views.start, name="start"),
    path("sorry", views.sorry, name="sorry"),
    path("calendar", views.calendar, name="calendar"),
    path("calendar/<str:date_param>", views.calendar, name="calendar"),
    path("stats", views.stats, name="stats"),
    path("stats/<str:date_param>", views.stats, name="stats"),
    path("auth/", views.auth, name="auth"),
    path("login", views.login, name="login"),
    path("admin", views.admin, name="admin"),
    path("studio/<int:pid>/", views.studio, name="studio"),
    path("day/<str:date_param>/", views.day, name="day"),
    path('update_play', views.update_play, name='update_play'),
    path('update_search', views.update_search, name="update_search"),
    path('get_flys', views.get_flys, name="get_flys"),
    path('get_path', views.get_path, name="get_path"),
    path('set_start', views.set_start, name="set_start"),
    path('get_dates', views.get_dates, name="get_dates")
]