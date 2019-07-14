from django.db import models

class Party(models.Model):
    name = models.CharField(max_length=100)
    roundNum = models.IntegerField(default = 0)
    roundTotal = models.IntegerField(default = 0)
    started = models.BooleanField(null = True)
    state = models.CharField(max_length=30, null =True)
    
    def __str__(self):
        return self.name

class Users(models.Model):
    name = models.CharField(max_length=35)
    party = models.ForeignKey('Party', on_delete=models.CASCADE,)
    sessionID = models.CharField(max_length = 200, null = True)
    points = models.IntegerField()
    isHost = models.BooleanField()
    hasSkip = models.BooleanField()
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

    def __str__(self):
        return self.name
