from celery import Celery
from celery.schedules import crontab

celery = Celery(
    "trekking_management",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=False,
    beat_schedule={
        "daily-trek-reminder": {
            "task": "tasks.daily_trek_reminder",
            "schedule": crontab(hour="8",minute="0")
        }
    }
)

def init_celery(app):
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

import tasks