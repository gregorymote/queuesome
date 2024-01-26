from django.db import models

# Create your models here.

class Fly(models.Model):
    album_name = models.CharField(max_length=255, null = True)
    album_url = models.CharField(max_length=255, null = True)
    artist_name = models.CharField(max_length=255, null = True)
    image_url = models.URLField(max_length=200)
    image = models.ImageField(upload_to='images/')
    x_coord = models.IntegerField(default = 1)
    y_coord = models.IntegerField(default = 1)
    x_mult = models.FloatField(default = 1)
    y_mult = models.FloatField(default = 1)
    color=models.CharField(max_length=128, default='130, 128, 131')
    date = models.DateField(null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, null=True)