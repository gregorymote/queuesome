# Generated by Django 2.2.3 on 2019-07-19 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0013_category_leader'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='roundNum',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='party',
            name='roundTotal',
            field=models.IntegerField(default=1),
        ),
    ]