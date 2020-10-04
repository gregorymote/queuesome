from django.urls import path
from game import views

urlpatterns = [
        path('<int:pid>/lobby/', views.lobby, name='lobby'),
        path('<int:pid>/lobby/code', views.code, name='code'),
        path('<int:pid>/play/', views.play, name='play'),
        path('<int:pid>/play/choose_category', views.chooseCat, name='choose_category'),
        path('<int:pid>/play/pick_song', views.pickSong, name='pick_song'),
        path('<int:pid>/play/pick_song/search_results', views.searchResults, name='search_results'),
        path('<int:pid>/play/round_results', views.roundResults, name='round_results'),
        path('<int:pid>/play/settings', views.settings, name='settings'),
        path('<int:pid>/play/users', views.users, name='users'),
        path('update_play', views.update_play, name='update_play'),
        path('update_game', views.update_game, name='update_game'),
        path('update_lobby', views.update_lobby, name='update_lobby'),
    ]
