from django.urls import path
from game import views

urlpatterns = [
        path('<int:pid>/lobby/', views.lobby, name='lobby'),
        path('<int:pid>/play/', views.play, name='play'),

    ]
