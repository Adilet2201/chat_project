from pathlib import Path
import environ

# ───────── env ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
env.read_env(BASE_DIR / ".env.dev")

# ───────── базовые настройки ────────────────────────────────
SECRET_KEY    = env("SECRET_KEY", default="dev-key")
DEBUG         = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

INSTALLED_APPS = [
    "chat_app.apps.ChatAppConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "chat_project.urls"
WSGI_APPLICATION = "chat_project.wsgi.application"

# ───────── templates ─────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "chat_app" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ───────── PostgreSQL ─────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE":  "django.db.backends.postgresql",
        "NAME":     env("POSTGRES_DB",       default="postgres"),
        "USER":     env("POSTGRES_USER",     default="postgres"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="postgres"),
        "HOST":     env("POSTGRES_HOST",     default="db"),
        "PORT":     env("POSTGRES_PORT",     default="5432"),
    }
}

# ───────── static ─────────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ───────── MinIO (S3 совместимое хранилище) ─────────────────────
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_S3_ENDPOINT_URL      = f"http://{env('MINIO_HOST')}:9000"  # Протокол HTTP!
AWS_ACCESS_KEY_ID        = env("MINIO_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY    = env("MINIO_SECRET_KEY")
AWS_STORAGE_BUCKET_NAME  = env("MINIO_BUCKET")                # имя бакета: django-bucket

AWS_S3_REGION_NAME       = "us-east-1"
AWS_S3_ADDRESSING_STYLE  = "path"
AWS_S3_SIGNATURE_VERSION = "s3v4"

AWS_DEFAULT_ACL          = "public-read"
AWS_QUERYSTRING_AUTH     = False

AWS_S3_USE_SSL           = False      # отключаем HTTPS
AWS_S3_SECURE_URLS       = False
AWS_S3_URL_PROTOCOL      = "http:"    # принудительно http

# Сконфигурировать публичный URL. Мы добавляем имя бакета в доменное имя:
AWS_S3_CUSTOM_DOMAIN     = "localhost:9000/django-bucket"
MEDIA_URL                = f"http://{AWS_S3_CUSTOM_DOMAIN}/"

# ───────── i18n ─────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "UTC"
USE_I18N      = True
USE_TZ        = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
