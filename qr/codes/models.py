import uuid
from django.db import models
from items.models import Item


class Code(models.Model):
    code = models.UUIDField(primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    item = models.ForeignKey(Item, blank=True, null=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return str(self.code)
