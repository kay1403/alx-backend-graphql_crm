# config/settings.py

INSTALLED_APPS = [
    # ... tes apps existantes ...
    'django_crontab',
]

CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]

# Celery config
INSTALLED_APPS += ['django_celery_beat']
CELERY_BROKER_URL = 'redis://localhost:6379/0'

from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
