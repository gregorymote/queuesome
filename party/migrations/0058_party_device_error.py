# Generated by Django 3.0.4 on 2020-07-17 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0057_auto_20200712_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='device_error',
            field=models.BooleanField(default=False),
        ),
    ]