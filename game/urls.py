from django.urls import path
from game import views

urlpatterns = [
        path('<int:pid>/lobby/', views.lobby, name='lobby'),
        path('<int:pid>/play/', views.play, name='play'),
        path('<int:pid>/play/choose_category', views.choose_category, name='choose_category'),
        path('<int:pid>/play/pick_song', views.pick_song, name='pick_song'),
        path('<int:pid>/play/pick_song/search_results', views.search_results, name='search_results'),
        path('<int:pid>/play/settings', views.settings, name='settings'),
        path('<int:pid>/play/users', views.users, name='users'),
        path('update_play', views.update_play, name='update_play'),
        path('update_game', views.update_game, name='update_game'),
        path('update_lobby', views.update_lobby, name='update_lobby'),
]
