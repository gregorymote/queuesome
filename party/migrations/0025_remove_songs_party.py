# Generated by Django 2.2.3 on 2019-08-02 18:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0024_songs_party'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='songs',
            name='party',
        ),
    ]
