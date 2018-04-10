from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

MEDIA_ROOT = '/mnt/video/images/'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tracker',
        'USER': 'tracker',
        'PASSWORD': 'tracker',
    }
}
