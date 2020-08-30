from django.db import models
from django_mysql.models import SetTextField
import spotipy

STRUCTURE_CHOICES = (
    ("{} in the Title", "{} in the Title"),
    ("Songs that {}", "Songs that {}"),
    ("Songs where {}", "Songs where {}"),
    ("{} Songs", "{} Songs"),
    ("Songs with {}","Songs with {}"),
    ("Songs from {}","Songs from {}"),
    ("Songs by {}","Songs by {}"),
    ("Songs {}", "Songs {}"),
    ("Songs about {}", "Songs about {}"),
    ("{}", "{}")
) 

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
    thread = models.BooleanField(default=False)
    device_error = models.BooleanField(default=False)
    active = models.BooleanField(default = True)
    last_updated = models.DateTimeField(auto_now=True, null=True)
    lib_repo = SetTextField(base_field=models.CharField(max_length=32), null=True)
    indices = SetTextField(base_field=models.CharField(max_length=32), null=True)
    debug = models.CharField(max_length=4000, null=True)

    def __str__(self):
        return self.name

class Users(models.Model):
    name = models.CharField(max_length=35)
    party = models.ForeignKey('Party', on_delete=models.CASCADE,)
    sessionID = models.CharField(max_length = 200, null = True)
    points = models.IntegerField(default=0)
    isHost = models.BooleanField(default=False)
    hasSkip = models.BooleanField(default=False)
    hasLiked = models.BooleanField(default=False)
    hasPicked = models.BooleanField(default = False)
    turn = models.CharField(max_length=20)
    active = models.BooleanField(default = True)
    refreshRate = models.IntegerField(default=5, null=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    roundNum = models.PositiveIntegerField(default = 0)
    party = models.ForeignKey('Party', on_delete=models.CASCADE,)
    leader = models.ForeignKey('Users',on_delete=models.SET_NULL, null=True)
    full = models.BooleanField(null=True, default=False)
    
    def __str__(self):
        return self.name
    

class Library(models.Model):
    name = models.CharField(max_length=100)
    display = models.CharField(max_length=120, default="No display name avaialable")
    structure = models.CharField(max_length=64, choices=STRUCTURE_CHOICES, default="{}")
    visible = models.BooleanField(default = False)
    special = models.BooleanField(default=False)
    order = models.IntegerField(default = 100)
    
    def save(self, *args, **kwargs): 
        self.display = self.structure.format(self.name) 
        super(Library, self).save(*args, **kwargs) 

    def __str__(self):
        return self.display
    
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
    debug = models.CharField(max_length=4000, null=True)
    link = models.CharField(max_length=500, null=True)
    duration=models.IntegerField(default=0, null=True)
    duplicate=models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Likes(models.Model):
    num = models.IntegerField(default=0)

    def __str__(self):
        return str(self.pk)

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
