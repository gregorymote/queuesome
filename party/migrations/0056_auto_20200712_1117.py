# Generated by Django 3.0.4 on 2020-07-12 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0055_auto_20200712_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='library',
            name='display',
            field=models.CharField(default='No display name avaialable', max_length=120),
        ),
    ]