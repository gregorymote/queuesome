from django.urls import path
from party import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('<int:pid>/start_party/', views.name_party, name='start_party'),
    path('join_party/', views.create_user, name='join_party'),
    path('auth/', views.auth, name='auth'),
    path('auth/complete/', views.complete, name='complete'),
    path('<int:pid>/choose_device/', views.choose_device, name='choose_device'),
    path('<int:pid>/your_code/<code>/', views.your_code, name='your_code'),
    
]
