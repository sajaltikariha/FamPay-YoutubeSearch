# Generated by Django 3.1.1 on 2020-09-10 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0003_auto_20200910_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='published_at',
            field=models.DateTimeField(),
        ),
    ]