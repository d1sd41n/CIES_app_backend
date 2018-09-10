from django.db import models
from django.db.models import Q

from core.models import Company

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

    @staticmethod
    def has_read_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group = request.user.groups.filter(Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.custom.seat.company_id)
        if group and user_company == parameters[0]:
            return True
        return False

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        return True

    @staticmethod
    def has_write_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group = request.user.groups.filter(Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.custom.seat.company_id)
        if group and user_company == parameters[0]:
            return True
        return False

    def __str__(self):
        return '{0} : {1}'.format(self.model, self.cause)
