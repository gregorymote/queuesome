from django.urls import path
from party import views

urlpatterns = [
    path('start_party/', views.name_party, name='start_party'),
    path('join_party/', views.create_user, name='join_party'),
]
