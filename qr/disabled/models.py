from django.db import models
from django.contrib.contenttypes.models import ContentType
from core.models import Company
from .managers import DisabledManager


class Disabled(models.Model):
    """Almacena los modelos que estan desactivados,
    el campo company sirve para saber que sierto objeto eliminado
    pertenece a una compañia, si es un compañia la que se desactiva, 
    el campo queda vacio"""
    model = models.ForeignKey(ContentType)
    cause = models.CharField(max_length=300, null=True, blank=True)
    date = models.DateField()
    fk_object = models.PositiveIntegerField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    objects = DisabledManager()

    def __str__(self):
        return '{0} : {1}'.format(self.model, self.cause)
