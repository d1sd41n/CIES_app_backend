from codes.managers import CodeManager
from core.models import Seat
from django.db import models
from django.db.models import Q
import uuid


class Code(models.Model):
    code = models.UUIDField(primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    enabled = models.BooleanField(default=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    objects = CodeManager()

    def has_read_permission(request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager") |
                                           Q(name="Security Boss"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        print(request.user)
        if group and user_company == parameters[0]:
            return True
        return False

    def has_object_read_permission(self, request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager") |
                                           Q(name="Security Boss"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        print(request.user)
        if group and user_company == parameters[0]:
            return True
        return False

    def has_object_write_permission(self, request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager") |
                                           Q(name="Security Boss"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        print(request.user)
        if group and user_company == parameters[0]:
            return True
        return False

    @staticmethod
    def has_write_permission(request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager") |
                                           Q(name="Security Boss"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        print(request.user)
        if group and user_company == parameters[0]:
            return True
        return False

    def __str__(self):
        return str(self.code)
