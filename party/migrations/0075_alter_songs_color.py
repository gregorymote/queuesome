# Generated by Django 3.2 on 2022-10-01 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0074_auto_20221001_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='songs',
            name='color',
            field=models.CharField(default='0,0,0', max_length=128),
        ),
    ]
