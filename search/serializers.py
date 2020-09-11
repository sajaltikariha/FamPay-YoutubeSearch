from .models import Video, User
from rest_framework import serializers

class VideoSerializer (serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'video_id', 'description', 'etag', 'thumbnail_url', 'published_at', 'channel_title']

class UserSerializer (serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'token', 'refresh_token']        