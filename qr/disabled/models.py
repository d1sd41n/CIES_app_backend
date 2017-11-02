from django.db import models
from django.contrib.contenttypes.models import ContentType


class Disabled(models.Model):
    """Almacena los modelos que estan desactivados"""
    model = models.ForeignKey(ContentType)
    cause = models.CharField(max_length=300)
    date = models.DateField()
    fk_object = models.PositiveIntegerField()

    def __str__(self):
        return '{0} : {1}'.format(self.model, self.cause)
