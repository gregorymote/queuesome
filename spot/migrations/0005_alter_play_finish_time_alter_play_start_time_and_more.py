# Generated by Django 4.1.7 on 2024-02-02 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spot', '0004_user_play'),
    ]

    operations = [
        migrations.AlterField(
            model_name='play',
            name='finish_time',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='play',
            name='start_time',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='play',
            name='time',
            field=models.TimeField(null=True),
        ),
    ]
