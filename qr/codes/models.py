import uuid
from django.db import models
from codes.managers import CodeManager
from core.models import Seat


class Code(models.Model):
    code = models.UUIDField(primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    used = models.BooleanField(default=False)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True)
    enabled = models.BooleanField(default=True)
    objects = CodeManager()

    def __str__(self):
        return str(self.code)
