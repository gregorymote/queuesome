from django.urls import path
from game import views
from party import views as p_views

urlpatterns = [
        path('<int:pid>/lobby/', views.lobby, name='lobby'),
        path('<int:pid>/play/', views.play, name='play'),
        path('<int:pid>/play/choose_category', views.choose_category, name='choose_category'),
        path('<int:pid>/play/pick_song', views.pick_song, name='pick_song'),
        path('<int:pid>/play/settings', views.settings, name='settings'),
        path('<int:pid>/play/users', views.users, name='users'),
        path('update_play', views.update_play, name='update_play'),
        path('update_lobby', views.update_lobby, name='update_lobby'),
        path('update_set_device', p_views.update_set_device, name='update_set_device'),
        path('update_search', views.update_search, name='update_search'),
        path('update_like', views.update_like, name='update_like'),
]
