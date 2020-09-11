import os
from celery import Celery
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youtube_search.settings')
 
app = Celery('youtube_search')
app.config_from_object('django.conf:settings')
 
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Task scheduler 
app.conf.beat_schedule = {
    "fetch-videos-every-ten-seconds-task": {
        "task": "search.views.fetch_videos_task",
        "schedule": 10.0 # 10 seconds 
    }
}