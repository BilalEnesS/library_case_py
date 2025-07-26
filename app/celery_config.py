from celery import Celery
from celery.schedules import crontab
import os

# Read broker URL from .env file
broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "tasks",
    broker=broker_url,
    backend=result_backend,
    include=["app.tasks"] # Specify the module containing tasks
)

# Celery Beat Scheduler
celery_app.conf.beat_schedule = {
    'send-overdue-reminders-daily': {
        'task': 'app.tasks.send_overdue_reminders',
        'schedule': crontab(hour=9, minute=0),  # Run every morning at 9 AM
    },
    # Weekly report is now generated manually from admin panel
    # 'generate-weekly-report': {
    #     'task': 'app.tasks.generate_weekly_report',
    #     'schedule': crontab(day_of_week='monday', hour=7, minute=30), # Every Monday 07:30
    # },
    'test-email-every-hour': {
        'task': 'app.tasks.send_test_email',
        'schedule': crontab(minute=0),  # Test email every hour (for development)
    },
}

celery_app.conf.timezone = 'UTC'

# Celery settings
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
)