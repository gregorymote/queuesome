# Generated by Django 4.1.7 on 2024-01-26 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spot', '0002_fly_x_mult_fly_y_mult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fly',
            name='x_mult',
            field=models.FloatField(default=1),
        ),
        migrations.AlterField(
            model_name='fly',
            name='y_mult',
            field=models.FloatField(default=1),
        ),
    ]