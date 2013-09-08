import os
from project.settings.base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES['default']['NAME'] = 'project_staging'

PUBLIC_ROOT = '/var/www/project-staging/public/'

STATIC_ROOT = os.path.join(PUBLIC_ROOT, 'static')

MEDIA_ROOT = os.path.join(PUBLIC_ROOT, 'media')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

EMAIL_SUBJECT_PREFIX = '[Project Staging] '

COMPRESS_ENABLED = True

SESSION_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True

ALLOWED_HOSTS = ('*')

# Uncomment if using celery worker configuration
# BROKER_URL = 'amqp://project:%s@127.0.0.1:5672/project_staging' % os.environ['BROKER_PASSWORD']

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ['SECRET_KEY']
