from pathlib import Path
import os

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-kilimo-hub-dev-key-change-in-production')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
_host_list = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')
_pythonanywhere = os.environ.get('PYTHONANYWHERE_HOSTNAME', '')
if _pythonanywhere and _pythonanywhere not in _host_list:
    _host_list.append(_pythonanywhere)
ALLOWED_HOSTS = [h.strip() for h in _host_list if h.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'crops',
    'market',
    'disease',
    'veterinary',
    'weather',
    'accounts',
    'translation',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kilimo_hub.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'kilimo_hub.wsgi.application'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'https://struggle-moonlight-arise.ngrok-free.app',
    'https://struggle-moonlight-arise.ngrok-free.dev',
    f'https://{os.environ.get("PYTHONANYWHERE_HOSTNAME", "MuyinzaSolomon10.pythonanywhere.com")}',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Kampala'
USE_I18N = True
USE_TZ = True
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', 'demo')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
SUNBIRD_API_URL = os.environ.get('SUNBIRD_API_URL', 'https://api.sunbird.ai/tasks/nllb_translate')
SUNBIRD_API_KEY = os.environ.get('SUNBIRD_API_KEY', '')

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
