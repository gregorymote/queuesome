# Generated by Django 3.0.4 on 2020-03-22 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0041_auto_20191129_0904'),
    ]

    operations = [
        migrations.AddField(
            model_name='searches',
            name='duration',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='songs',
            name='duration',
            field=models.IntegerField(default=0, null=True),
        ),
    ]