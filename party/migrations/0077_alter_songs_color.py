# Generated by Django 3.2.16 on 2022-10-30 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0076_alter_songs_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='songs',
            name='color',
            field=models.CharField(default='130, 128, 131', max_length=128),
        ),
    ]
