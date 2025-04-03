import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Инициируем django-environ
env = environ.Env(
    DEBUG=(bool, False),
)
# Попытка загрузить .env (по умолчанию .env.dev)
env_file = os.path.join(BASE_DIR, '..', '.env.dev')
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

SECRET_KEY = env('SECRET_KEY', default='django-insecure-default')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

INSTALLED_APPS = [
    'chat_app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'storages',  # если нужно для MinIO/S3
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chat_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'chat_app' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # нужно для auth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chat_project.wsgi.application'

# Подключаем PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB', default='postgres'),
        'USER': env('POSTGRES_USER', default='postgres'),
        'PASSWORD': env('POSTGRES_PASSWORD', default='postgres'),
        'HOST': env('POSTGRES_HOST', default='db'),
        'PORT': env('POSTGRES_PORT', default='5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },{
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },{
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },{
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # при collectstatic всё сложим сюда

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# MinIO / S3 settings (пример)
USE_MINIO = env.bool('USE_MINIO', default=False)
if USE_MINIO:
    INSTALLED_APPS += ['storages']
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_S3_ENDPOINT_URL = f"http://{env('MINIO_HOST')}:9000"
    AWS_ACCESS_KEY_ID = env('MINIO_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = env('MINIO_SECRET_KEY')
    AWS_STORAGE_BUCKET_NAME = env('MINIO_BUCKET')
    AWS_S3_REGION_NAME = 'us-east-1'
    AWS_S3_SIGNATURE_VERSION = 's3v4'
