# Generated by Django 3.1.1 on 2020-09-10 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField()),
                ('refresh_token', models.TextField(null=True)),
                ('toker_uri', models.TextField()),
                ('client_id', models.TextField()),
                ('client_secret', models.TextField()),
                ('scopes', models.TextField()),
            ],
        ),
    ]
