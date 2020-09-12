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
from youtube_search.celery import app

#imports from db
from .models import Video, User

#imports from serializer
from .serializers import VideoSerializer, UserSerializer

CLIENT_SECRETS_FILE = 'search/client_secret.json'
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# Create your views here.

"""
Background task to fetch latest videos every 10 seconds
"""
@app.task
def fetch_videos_task():
    cred = User.objects.last()
    latest_video = Video.objects.order_by("-published_at").first()
    credentials = google.oauth2.credentials.Credentials(
        token = cred.token,
        refresh_token = cred.refresh_token,
        token_uri = cred.token_uri, 
        client_id = cred.client_id,
        client_secret = cred.client_secret,
        scopes = cred.scopes,
    )
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials = credentials)
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
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes = SCOPES, state = state)
    flow.redirect_uri = "https://" + request.META.get('HTTP_HOST') + '/oauth-callback'
    url = "https://" + request.META.get('HTTP_HOST') + request.get_full_path()
    flow.fetch_token(authorization_response = url)
    credentials = flow.credentials # get required credentials 
    user = User()
    user.token = credentials.token
    user.refresh_token = credentials.refresh_token
    user.token_uri = credentials.token_uri
    user.client_id = credentials.client_id
    user.client_secret = credentials.client_secret
    user.scopes = credentials.scopes
    user.save()

    """
    Here first cached response is used just to check if we are getting a proper response or not (for testing purpose)
    otherwise all the responses would be made in background only. 
    """
    youtube = googleapiclient.discovery.build( 
        API_SERVICE_NAME, API_VERSION, credentials = credentials)
    request = youtube.search().list(
        part = "snippet",
        order = "date",
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
    return JsonResponse(response, status = 200)

"""
Authorization funtion
"""
def authorize(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    flow.redirect_uri = "https://" + request.META.get('HTTP_HOST') + '/oauth-callback'

    authorization_url, state = flow.authorization_url(
        access_type = 'offline',
        include_granted_scopes = 'true'
    )
    return HttpResponseRedirect(authorization_url)

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
Latest videos api-call component with search query option
"""
class VideoViewset(APIView):
    serializer_class = VideoSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get(self, request):
        search_query = self.request.GET.get('query')
        videos_list = Video.objects.order_by("-published_at")
        if search_query:
            search_results = []
            for video in videos_list:
                title = video.title.lower()
                description = video.description.lower()
                if ((title.find(search_query.lower()) != -1) or (description.find(search_query.lower()) != -1)):
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



