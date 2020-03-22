from django.db import models
import spotipy

class Party(models.Model):
    name = models.CharField(max_length=100, null = True)
    token = models.CharField(max_length=1000, null = True)
    token_info = models.CharField(max_length=1000, null = True)
    code = models.CharField(max_length=10, null = True)
    url = models.CharField(max_length=1000, null = True)
    url_open = models.CharField(max_length=999, null = True)
    roundNum = models.IntegerField(default = 1)
    roundTotal = models.IntegerField(default = 1)
    started = models.BooleanField(null = True)
    state = models.CharField(max_length=30, null =True)
    deviceID = models.CharField(max_length=200, null=True)
    time = models.IntegerField(default=80)
    joinCode = models.CharField(max_length=10, null = True)
    active = models.BooleanField(default = True)
    
    def __str__(self):
        return self.name

class Users(models.Model):
    name = models.CharField(max_length=35)
    party = models.ForeignKey('Party', on_delete=models.CASCADE,)
    sessionID = models.CharField(max_length = 200, null = True)
    points = models.IntegerField()
    isHost = models.BooleanField()
    hasSkip = models.BooleanField()
    hasLiked = models.BooleanField(default=False)
    hasPicked = models.BooleanField(default = False)
    turn = models.CharField(max_length=20)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    roundNum = models.PositiveIntegerField(default = 0)
    party = models.ForeignKey('Party', on_delete=models.CASCADE,)
    leader = models.ForeignKey('Users',on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.name

class Library(models.Model):
    name = models.CharField(max_length=100)
    visible = models.BooleanField(default = False)

    def __str__(self):
        return self.name
    
class Songs(models.Model):
    name = models.CharField(max_length=500)
    uri = models.CharField(max_length=500)
    art = models.CharField(max_length=500)
    user = models.ForeignKey('Users',on_delete=models.CASCADE,)
    category = models.ForeignKey('Category',on_delete=models.CASCADE,)
    played = models.BooleanField(default = False)
    order = models.IntegerField(default = 0)
    state = models.CharField(max_length=10, default='not_played')
    startTime= models.FloatField(default=0)
    likes = models.ForeignKey('Likes',on_delete=models.CASCADE,)
    debug = models.CharField(max_length=1200, null=True)
    link = models.CharField(max_length=500, null=True)
    duration=models.IntegerField(default=0, null=True)
    duplicate=models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Likes(models.Model):
    num = models.IntegerField(default=0)

class Devices(models.Model):
    name = models.CharField(max_length=100)
    deviceID = models.CharField(max_length=200)
    party = models.ForeignKey('Party', on_delete=models.CASCADE,)

    def __str__(self):
        return self.name

class Searches(models.Model):
    name = models.CharField(max_length=500)
    uri = models.CharField(max_length=500)
    art = models.CharField(max_length=500, null=True)
    party = models.ForeignKey('Party', on_delete=models.CASCADE,)
    user = models.ForeignKey('Users',on_delete=models.CASCADE,)
    link = models.CharField(max_length=500, null=True)
    duration=models.IntegerField(default=0, null=True)
    def __str__(self):
        return self.name
