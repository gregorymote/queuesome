# Generated by Django 3.0.4 on 2020-03-28 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0044_users_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='library',
            name='order',
            field=models.IntegerField(default=100),
        ),
    ]
