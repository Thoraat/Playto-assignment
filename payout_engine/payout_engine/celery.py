import os
from celery import Celery
from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payout_engine.settings')

app = Celery('payout_engine')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()