from project.settings.staging import *

# There should be only minor differences from staging

DATABASES['default']['NAME'] = 'project_production'

PUBLIC_ROOT = '/var/www/project-production/public/'

STATIC_ROOT = os.path.join(PUBLIC_ROOT, 'static')

MEDIA_ROOT = os.path.join(PUBLIC_ROOT, 'media')

EMAIL_SUBJECT_PREFIX = '[Project Prod] '

# Uncomment if using celery worker configuration
# BROKER_URL = 'amqp://project:%s@127.0.0.1:5672/project_production' % os.environ['BROKER_PASSWORD']
