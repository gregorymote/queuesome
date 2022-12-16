from django.urls import path
from party import views

urlpatterns = [
    path('<int:pid>/start_party/', views.name_party, name='start_party'),
    path('join_party/', views.join_party, name='join_party'),
    path('auth/', views.auth, name='auth'),
    path('<int:pid>/choose_device/', views.choose_device, name='choose_device'),
    path('<int:pid>/set_device/', views.set_device, name='set_device'),
    path('update_devices', views.update_devices, name='update_devices'),
    path('update_set_device', views.update_set_device, name='update_set_device'),
    path('validate_code', views.validate_code, name='validate_code'),
    
]
