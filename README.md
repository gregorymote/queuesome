# Queue it Up
Spotipy/Django Web Application Game

#Create virtual environment and install django

#In desired directory run

python -m venv venv
 
#activate virutal environment 
 
C:\> venv\Scripts\activate.bat

#Install Django

(venv) $ pip install Django

#Useful Django tutorial for additional help https://realpython.com/get-started-with-django-1/


#Additional libraries needed

#install spotipy

pip install spotipy

pip install git+https://github.com/plamere/spotipy.git --upgrade

#add util_custom to \Lib\site-packages\spotipy

#add value of client secret to client secret variable at the top of party/views.py

#Note: client secret has been removed from github to abide by Spotify's terms and conditions

#To Create Access to other Devices from Your IP Address

edit party/view and change my_IP and my_PORT at the top of the page

edit queue_it_up/settings and change

#From cmd line run
python manage.py runserver 0.0.0.0:<value of my_PORT>
