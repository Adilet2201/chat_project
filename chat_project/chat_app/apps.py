# chat_app/apps.py
from django.apps import AppConfig

class ChatAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat_app'

    def ready(self):
        # Import the function here to avoid circular imports.
        from .minio_utils import create_minio_bucket
        create_minio_bucket()
