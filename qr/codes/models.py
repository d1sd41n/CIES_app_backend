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

    def has_read_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group = request.user.groups.filter(Q(name="Manager") |
                                           Q(name="Security Boss"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company.id)
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
        group = request.user.groups.filter(Q(name="Manager") |
                                           Q(name="Security Boss"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company.id)
        if group and user_company == parameters[0]:
            return True
        return False

    def __str__(self):
        return str(self.code)
