from django.urls import path
from game import views

urlpatterns = [
        path('<int:pid>/lobby/', views.lobby, name='lobby'),
        path('<int:pid>/play/', views.play, name='play'),
        path('<int:pid>/play/choose_category', views.chooseCat, name='choose_category'),
        path('<int:pid>/play/pick_song', views.pickSong, name='pick_song'),
        path('<int:pid>/play/pick_song/search_results', views.searchResults, name='search_results'),
    ]
