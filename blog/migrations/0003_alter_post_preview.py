# Generated by Django 3.2.4 on 2021-06-27 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_post_preview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='preview',
            field=models.TextField(blank=True, default='', max_length=200),
        ),
    ]
