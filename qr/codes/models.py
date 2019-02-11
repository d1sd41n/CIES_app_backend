import uuid

from django.db import models
from django.db.models import Q

from codes.managers import CodeManager
from core.models import CustomUser, Seat


class Code(models.Model):
    code = models.UUIDField(primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    enabled = models.BooleanField(default=True)
    seat = models.ForeignKey(Seat,
                             on_delete=models.CASCADE,
                             null=True)
    used = models.BooleanField(default=False)
    objects = CodeManager()

    def __str__(self):
        return str(self.code)
