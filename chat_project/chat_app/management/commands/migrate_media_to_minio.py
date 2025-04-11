"""
Move every file that still lives on local disk (settings.MEDIA_ROOT)
into the current DEFAULT_FILE_STORAGE (MinIO) and update database
references so future requests use the new URL.

Run once inside the web container:

    docker compose exec web python manage.py migrate_media_to_minio
"""

from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import transaction

from chat_app import models as m


# ---------------------------------------------------------------------------
# Which models & fields contain FileField / ImageField references?
# Add new tuples here if you introduce more file‑holding fields later.
# ---------------------------------------------------------------------------
FILE_FIELDS = [
    (m.Profile, "profile_pic"),
    (m.Message, "image"),
    (m.Post,    "image"),
]

MEDIA_ROOT = Path(settings.MEDIA_ROOT)


class Command(BaseCommand):
    help = (
        "Copy all media files that are still on local disk to MinIO (or "
        "whatever DEFAULT_FILE_STORAGE points to) and save the models so their "
        "paths remain unchanged."
    )

    def handle(self, *args, **options):
        copied = skipped = 0

        for model, field_name in FILE_FIELDS:
            qs = model.objects.exclude(**{field_name: ""})

            for obj in qs.iterator():
                file_field = getattr(obj, field_name)
                local_path = MEDIA_ROOT / file_field.name

                # If the file doesn't exist locally, assume it's already remote
                if not local_path.exists():
                    skipped += 1
                    continue

                self.stdout.write(f"→ uploading {file_field.name}")
                with local_path.open("rb") as fp:
                    # Same name => uploaded to MinIO, overwriting if needed
                    default_storage.save(file_field.name, fp)

                # Prevent Django from deleting the just‑uploaded file on save()
                file_field._committed = True
                copied += 1

            # Commit any changed objects in a single transaction
            with transaction.atomic():
                for obj in qs:
                    obj.save(update_fields=[field_name])

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished. Copied {copied} file(s), skipped {skipped} already‑remote file(s)."
            )
        )
