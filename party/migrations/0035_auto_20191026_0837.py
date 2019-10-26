# Generated by Django 2.2.6 on 2019-10-26 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0034_songs_likes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='songs',
            name='likes',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='party.Likes'),
        ),
    ]
