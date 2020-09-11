import os
import uuid

from django.db import models

# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    video_id = models.TextField(null=False, blank=False)
    etag = models.TextField(null=False, blank=False)
    description = models.CharField(max_length=1000, null=False, blank=False)
    channel_title = models.CharField(max_length=50, null=False, blank=False)
    thumbnail_url = models.TextField(null=False, blank=False)
    published_at = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.title

class User(models.Model):
    token = models.TextField(null=False, blank=False)
    refresh_token = models.TextField(null=True, blank=False)
    token_uri = models.TextField(null=False, blank=False)
    client_id = models.TextField(null=False, blank=False)
    client_secret = models.TextField(null=False, blank=False)
    scopes = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.token