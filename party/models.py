from django.db import models

class Party(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, null = True)
    started = models.BooleanField(null = True)
    
    def __str__(self):
        return self.name

class Users(models.Model):
    name = models.CharField(max_length=35)
    party = models.ForeignKey('Party', on_delete=models.CASCADE,)
    sessionID = models.CharField(max_length = 200, null = True)
    points = models.IntegerField()
    isHost = models.BooleanField()
    hasSkip = models.BooleanField()
    state = models.CharField(max_length=20)
    turn = models.CharField(max_length=20)
    def __str__(self):
        return self.name
