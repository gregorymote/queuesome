from django.contrib.postgres.fields import ArrayField
from django.db import models

# Create your models here.

class Day(models.Model):
    date = models.DateField(null=True)
    fly = models.ForeignKey('Fly', on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.date or ''

class Fly(models.Model):
    album_name = models.CharField(max_length=255, null = True)
    album_id = models.CharField(max_length=255, null = True)
    album_url = models.CharField(max_length=255, null = True)
    artist_name = models.CharField(max_length=255, null = True)
    artwork_url = models.CharField(max_length=255, null = True)
    image = models.ImageField(upload_to='images/')
    x_coord = models.IntegerField(default = 1)
    y_coord = models.IntegerField(default = 1)
    x_mult = models.FloatField(default=0)
    y_mult = models.FloatField(default=0)
    width = models.FloatField(default=0)
    color=models.CharField(max_length=128, default='130, 128, 131')
    fly_color = models.CharField(max_length=128, default='#FFFFFF')
    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, null=True)
    def __str__(self):
        return self.album_name or ''

class Users(models.Model):
    sessionID = models.CharField(max_length = 255, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_visited = models.DateTimeField(auto_now=True, null=True)
    

class Play(models.Model):
    start_time = models.TimeField(null=True)
    finish_time = models.TimeField(null=True)
    time = models.TimeField(null=True) 
    x_mult = models.FloatField(default=0)
    y_mult = models.FloatField(default=0)
    path = ArrayField(ArrayField(models.IntegerField()), null=True)
    pathm = ArrayField(ArrayField(models.FloatField()), null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, null=True)
    day = models.ForeignKey('Day', on_delete=models.CASCADE, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE,)


from django.contrib.auth.models import User

class Studio(models.Model):
    token_info = models.CharField(max_length=1000, null = True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)