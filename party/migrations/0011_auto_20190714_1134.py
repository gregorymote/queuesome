# Generated by Django 2.2.3 on 2019-07-14 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0010_auto_20190714_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='roundTotal',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='party',
            name='state',
            field=models.CharField(max_length=30, null=True),
        ),
    ]