"""
Django settings for django_starko project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import os
from .settings_local import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS


TEMPLATE_CONTEXT_PROCESSORS = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

import subprocess

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w==p1ti-e#evw(w3&2z0ty$1e9_syhwi7in_71w=@(_&p77zuy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']

LOGIN_REDIRECT_URL = '/'
# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mc',
    'django.contrib.admin',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    "django.core.context_processors.request",
    "mc.context_processors.show_version",
    "mc.context_processors.show_tz",

    'django.template.context_processors.debug',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

TEMPLATES = [
     {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "mc.context_processors.show_version",
                "mc.context_processors.show_tz",
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',]
        },
    },
]


ROOT_URLCONF = 'django_starko.urls'

WSGI_APPLICATION = 'django_starko.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASESx = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'django_starko',
        'USER': 'django_starko',
        'PASSWORD': 'qwerty1',
        'HOST': 'localhost',
        'PORT': '3306',
        'CONN_MAX_AGE': 3600,
        'OPTIONS': {
            'autocommit': True,
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = '/var/www/static'
LOGIN_REDIRECT_URL = '/mc'
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

MEDIA_ROOT = '/var/www/media'

MEDIA_URL = '/media/'

MC_HOSTS_USER = 'root'
MC_HOSTS_PASSWORD = 'Little0pte0'
MC_LOCAL_FILES_ROOT = '/var/www'
MC_LOCAL_FILES_DIR = '/var/www/media'
MC_LOCAL_BUFFER_DIR = '/var/www/buffer'

MC_WORK_USER = 'starko'
MC_WORK_USER_PASSWORD = 'starko'
MC_SSH_PORT = 22
SSH_TIMEOUT = 5.0

MC_PATCH_FOLDER = 'patch'
MC_NGINX_TMP = '/tmp/upload'

EMC_HOST_URL = 'https://opteo.pro'
EMC_SSH_ADDRESS = 'opteo.pro'
EMC_SSH_PORT = '22022'
EMC_BACKDOOR_USER = 'opteo_local'
EMC_BACKDOOR_PASSWORD = 'LittleBackd0re'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGIN_URL = '/login/'


def _detect_timezone_etc_timezone():
    if os.path.exists("/etc/timezone"):
        try:
            tz = open("/etc/timezone", 'w').read().strip()
            print(tz)
            try:
                return tz
            except IOError as ei:
                return None

        # Problem reading the /etc/timezone file
        except IOError as eo:
            return None


TIME_ZONE = _detect_timezone_etc_timezone() or TIME_ZONE

ALLOWED_TZS = ['Asia/Magadan',
               'Asia/Kamchatka',
               'Asia/Irkutsk',
               'Asia/Vladivostok',
               'Asia/Yakutsk',
               'Asia/Omsk',
               'Asia/Krasnoyarsk',
               'Asia/Yekaterinburg',
               'Europe/Kaliningrad',
               'Europe/Moscow']


def _uuid():
    return subprocess.check_output("cat /proc/cpuinfo | grep ^Serial | awk {'print $3'}", stderr=subprocess.STDOUT,
                                   shell=True).decode("utf-8")


def _bluetooth():
    return subprocess.check_output("ls /home/starko |grep bluetoothctl.py | awk {'print $1'}", stderr=subprocess.STDOUT,
                                   shell=True).decode("utf-8")


UUID = _uuid()
BT_ON = True if _bluetooth() else False

if not MEDIA_ROOT:
    raise Exception('MEDIA_ROOT setting not configured!!!')


def get_version_s():
    ver_file_path = os.path.join(MEDIA_ROOT, MC_PATCH_FOLDER, '.service', '.ver')
    try:
        try:
            with open(ver_file_path) as f:
                ver = f.readline().replace('\n', '')
                return ver
        except:
            with open(ver_file_path, "a") as myfile:
                myfile.write("1.0")
                myfile.write('\n')
                return "1.0"
    except:
        return '-'


MC_VERSION = get_version_s()

BITRATE_LIMIT = 16000000
