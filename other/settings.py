"""
Django settings for django_starko project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


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
    "mc.context_processors.show_tz"
)

ROOT_URLCONF = 'django_starko.urls'

WSGI_APPLICATION = 'django_starko.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
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
MC_LOCAL_FILES_ROOT = '/var/starko'
MC_LOCAL_FILES_DIR = '/var/starko/media'
MC_LOCAL_BUFFER_DIR = '/var/starko/buffer'

MC_WORK_USER = 'starko'
MC_WORK_USER_PASSWORD = 'starko'
MC_SSH_PORT = 22
SSH_TIMEOUT = 5

MC_PATCH_FOLDER = 'patch'
MC_NGINX_TMP = '/tmp/upload'

EMC_HOST_URL = 'https://opteo.pro'
EMC_SSH_ADDRESS = 'opteo.pro'
EMC_SSH_PORT = '22022'
EMC_BACKDOOR_USER = 'opteo_local'
EMC_BACKDOOR_PASSWORD = 'LittleBackd0re'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGIN_URL = '/login/'

def get_version_s():
    ver_file_path = os.path.join(MEDIA_ROOT, MC_PATCH_FOLDER, '.service', '.ver')
    try:
        with open(ver_file_path) as f:
            ver = f.readline().replace('\n', '')
            return ver
    except:
        with open(ver_file_path, "a") as myfile:
            myfile.write("1.0")
            myfile.write('\n')
            return "1.0"

MC_VERSION = get_version_s()


def _detect_timezone_etc_timezone():
    if os.path.exists("/etc/timezone"):
        try:
            tz = file("/etc/timezone").read().strip()
            try:
                return tz
            except IOError, ei:
                return None

        # Problem reading the /etc/timezone file
        except IOError, eo:
            return None

TIME_ZONE = _detect_timezone_etc_timezone()

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
    return subprocess.check_output("cat /proc/cpuinfo | grep ^Serial | awk {'print $3'}", stderr=subprocess.STDOUT, shell=True)

def _bluetooth():
    return subprocess.check_output("ls /home/starko |grep bluetoothctl.py | awk {'print $1'}", stderr=subprocess.STDOUT,
                                   shell=True)

UUID = _uuid()
BT_ON = True if _bluetooth() else False

BITRATE_LIMIT = 20000000

try:
    from settings_local import *
except ImportError:
    pass