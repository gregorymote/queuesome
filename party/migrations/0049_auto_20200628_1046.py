# Generated by Django 3.0.4 on 2020-06-28 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0048_users_refreshrate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='refreshRate',
            field=models.IntegerField(default=5, null=True),
        ),
    ]