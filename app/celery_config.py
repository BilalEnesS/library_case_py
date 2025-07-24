from celery import Celery
from celery.schedules import crontab
import os

# .env dosyasından broker URL'sini oku
broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "tasks",
    broker=broker_url,
    backend=result_backend,
    include=["app.tasks"] # Görevlerin bulunduğu modülü belirt
)

# Celery Beat Zamanlayıcısı
celery_app.conf.beat_schedule = {
    'send-reminders-every-day': {
        'task': 'app.tasks.send_overdue_reminders',
        'schedule': crontab(hour=9, minute=0),  # Her sabah 9'da çalıştır
    },
    'generate-report-every-week': {
        'task': 'app.tasks.generate_weekly_report',
        'schedule': crontab(day_of_week='monday', hour=7, minute=30), # Her Pazartesi 07:30
    },
}
celery_app.conf.timezone = 'UTC'