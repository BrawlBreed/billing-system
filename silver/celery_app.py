# # silver/celery_app.py
# import os
# from celery import Celery  # Import from main celery package, not from self

# # Set the default Django settings module for the 'celery' program
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# app = Celery('silver')

# # Using a string here means the worker doesn't have to serialize
# # the configuration object to child processes.
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Load task modules from all registered Django app configs
# app.autodiscover_tasks()

# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
app = Celery("silver")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()  # без ръчни импорти на tasks
