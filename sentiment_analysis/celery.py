from __future__ import absolute_import
import os

from celery import Celery
from kombu import Exchange, Queue
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentiment_analysis.settings')

app = Celery('sentiment_analysis')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
queue = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('machine1', Exchange('machine1'), routing_key='machine1'),
    Queue('machine2', Exchange('machine2'), routing_key='machine2'),
)

app.conf.update(CELERY_QUEUES=queue,
                CELERY_ROUTES={
                    'backend.tasks.add_machine1': {'queue': 'machine1'},
                    'backend.tasks.add_machine2': {'queue': 'machine2'},
                    'backend.tasks.crawl_machine1': {'queue': 'machine1'},
                    'backend.tasks.crawl_machine2': {'queue': 'machine2'},
                },

                )
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))  
