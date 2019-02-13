from django.db import models
from django.db.models import Q

from core.models import Company, CustomUser

from .managers import DisabledManager

MODEL_CHOICE = (
    ('brand', 'Brand'),
    ('item', 'Item'),
    ('lostitem', 'Lost Item'),
    ('typeitem', 'Type Item'),
    ('visitor', 'Visitor'))


class Disabled(models.Model):
    """Almacena los modelos que estan desactivados,
    el campo company sirve para saber que cierto objeto eliminado
    pertenece a una compañía, si es un compañía la que se desactiva,
    el campo queda vacío"""
    action = models.NullBooleanField(choices=((True, "Enable"),
                                              (False, "Disable")), default=True)
    cause = models.CharField(max_length=300, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True, blank=True)
    fk_object = models.PositiveIntegerField()
    model = models.CharField(max_length=13, choices=MODEL_CHOICE)
    objects = DisabledManager()

    def __str__(self):
        return '{0} : {1}'.format(self.model, self.cause)
