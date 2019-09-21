# Generated by Django 2.2.3 on 2019-07-28 23:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0021_searches'),
    ]

    operations = [
        migrations.CreateModel(
            name='Songs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('uri', models.CharField(max_length=500)),
                ('art', models.CharField(max_length=500)),
                ('played', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='party.Category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='party.Users')),
            ],
        ),
    ]