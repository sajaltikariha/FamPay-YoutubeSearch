# Generated by Django 3.1.1 on 2020-09-10 20:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0002_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='toker_uri',
            new_name='token_uri',
        ),
    ]