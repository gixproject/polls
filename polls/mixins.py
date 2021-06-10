import uuid

from django.db import models


class UUIDMixin(models.Model):
    """
    AbstractMode that replace default id type from Auto-Increment to UUID.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
