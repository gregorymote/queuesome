# Generated by Django 5.0.2 on 2024-03-01 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spot', '0022_remove_fly_file_remove_fly_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='play',
            name='give_up',
            field=models.BooleanField(default=False),
        ),
    ]
