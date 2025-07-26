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
    'send-overdue-reminders-daily': {
        'task': 'app.tasks.send_overdue_reminders',
        'schedule': crontab(hour=9, minute=0),  # Her sabah 9'da çalıştır
    },
    # Haftalık rapor artık manuel olarak admin panelinden oluşturulacak
    # 'generate-weekly-report': {
    #     'task': 'app.tasks.generate_weekly_report',
    #     'schedule': crontab(day_of_week='monday', hour=7, minute=30), # Her Pazartesi 07:30
    # },
    'test-email-every-hour': {
        'task': 'app.tasks.send_test_email',
        'schedule': crontab(minute=0),  # Her saat başı test email'i (geliştirme için)
    },
}

celery_app.conf.timezone = 'UTC'

# Celery ayarları
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 dakika
)