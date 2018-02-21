import uuid
from django.db import models
from codes.managers import CodeManager


class Code(models.Model):
    code = models.UUIDField(primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    used = models.BooleanField(default=False)
    objects = CodeManager()

    def __str__(self):
        return str(self.code)
