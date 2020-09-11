from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.settings import api_settings

#imports for google authentication and authorization
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import google.oauth2.credentials

#imports for celery/bacground task execution
import logging
from youtube_search.celery import app

#imports from db
from .models import Video, User

#imports from serializer
from .serializers import VideoSerializer, UserSerializer

client_secrets_file = 'search/client_secret.json'
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
api_service_name = "youtube"
api_version = "v3"

HOSTNAME = 'https://dd91e1e366ad.ngrok.io'

# Create your views here.

"""
Background task to fetch latest videos every 10 seconds
"""
@app.task
def fetch_videos_task():
    logging.debug("Reached Task")
    cred = User.objects.last()
    latest_video = Video.objects.order_by("-published_at").first()
    CREDENTIALS = google.oauth2.credentials.Credentials(
        token = cred.token,
        refresh_token = cred.refresh_token,
        token_uri = cred.token_uri, 
        client_id = cred.client_id,
        client_secret = cred.client_secret,
        scopes = cred.scopes,
    )
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials = CREDENTIALS)
    request = youtube.search().list(
        part = "snippet",
        order = "date",
        publishedAfter = latest_video.published_at,
        type = "video",
    )
    response = request.execute()
    for item in response['items']:
        video = Video()
        video.video_id = item['id']['videoId']
        video.title = item['snippet']['title']
        video.description = item['snippet']['description']
        video.etag = item['etag']
        video.channel_title = item['snippet']['channelTitle']
        video.thumbnail_url = item['snippet']['thumbnails']['default']['url']
        video.published_at = item['snippet']['publishedAt']
        video.save()

"""
O Auth 2.0 callback function
"""
def oauth_callback(request):
    state = request.GET.get('state')
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(client_secrets_file, scopes = scopes, state = state)
    flow.redirect_uri = "https://" + request.META.get('HTTP_HOST') + '/oauth-callback'
    url = "https://" + request.META.get('HTTP_HOST') + request.get_full_path()
    flow.fetch_token(authorization_response = url)
    CREDENTIALS = flow.credentials # get required credentials 
    user = User()
    user.token = CREDENTIALS.token
    user.refresh_token = CREDENTIALS.refresh_token
    user.token_uri = CREDENTIALS.token_uri
    user.client_id = CREDENTIALS.client_id
    user.client_secret = CREDENTIALS.client_secret
    user.scopes = CREDENTIALS.scopes
    user.save()
    youtube = googleapiclient.discovery.build( 
        api_service_name, api_version, credentials = CREDENTIALS)
    request = youtube.search().list(
        part = "snippet",
        order = "date",
        type = "video",
    )
    response = request.execute()[:5]
    for item in response['items']:
        video = Video()
        video.video_id = item['id']['videoId']
        video.title = item['snippet']['title']
        video.description = item['snippet']['description']
        video.etag = item['etag']
        video.channel_title = item['snippet']['channelTitle']
        video.thumbnail_url = item['snippet']['thumbnails']['default']['url']
        video.published_at = item['snippet']['publishedAt']
        video.save()
    return JsonResponse(response, status = 200)

"""
Authorization funtion
"""
def authorize(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(client_secrets_file, scopes)
    flow.redirect_uri = "https://" + request.META.get('HTTP_HOST') + '/oauth-callback'

    authorization_url, state = flow.authorization_url(
        access_type = 'offline',
        include_granted_scopes = 'true'
    )

    return HttpResponseRedirect(authorization_url)

"""
Latest videos api-call component
"""  
class VideoViewset(APIView):
    queryset = Video.objects.order_by("-published_at")
    serializer_class = VideoSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    """
    request handler function 
    """
    def get(self, request):
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.serializer_class(page, many = True)
            return JsonResponse(serializer.data, safe = False)
    
    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view = self)

"""
User info api-call component (Just for testing purpose)
"""
class UserViewset(APIView):
    serializer_class = UserSerializer

    def get(self, request):
        users = User.objects.all().order_by("id") 
        serializer = self.serializer_class(users, many = True)
        return JsonResponse(serializer.data, safe = False)

"""
Search videos api-call component
"""
class SearchViewset(APIView):
    serializer_class = VideoSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get(self, request):
        search_query = self.request.GET.get('query')
        videos_list = Video.objects.order_by("-published_at")
        if search_query:
            search_results = Video.objects.none()
            for video in videos_list:
                title = video.title
                description = video.description
                if ((title.find(search_query) != -1) or (description.find(search_query) != -1)):
                    search_results.append(video)
            page = self.paginate_queryset(search_results)      
        else:
            page = self.paginate_queryset(videos_list)
        
        if page is not None:
            serializer = self.serializer_class(page, many = True) 
            return JsonResponse(serializer.data, safe = False)
            
        @property
        def paginator(self):
            """
            The paginator instance associated with the view, or `None`.
            """
            if not hasattr(self, '_paginator'):
                if self.pagination_class is None:
                    self._paginator = None
                else:
                    self._paginator = self.pagination_class()
            return self._paginator

        def paginate_queryset(self, queryset):
            """
            Return a single page of results, or `None` if pagination is disabled.
            """
            if self.paginator is None:
                return None
            return self.paginator.paginate_queryset(queryset, self.request, view = self)



