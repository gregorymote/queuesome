# Generated by Django 2.2.6 on 2019-11-16 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0037_remove_party_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='searches',
            name='link',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='songs',
            name='link',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
