from django.urls import path
from party import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('<int:pid>/start_party/', views.name_party, name='start_party'),
    path('join_party/', views.create_user, name='join_party'),
    path('auth/', views.auth, name='auth'),
    path('<int:pid>/choose_device/', views.choose_device, name='choose_device'),
    path('check_devices', views.check_devices, name='check_devices'),
    
]
