from core.managers import (
                            CustomUserManager,
                            CompanyManager,
                            SeatManager,
                            VisitorManager,
                            )
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from ubication.models import Location


class Company(models.Model):
    """Almacena datos generales de una empresa.
    """
    nit = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=100, unique=True)
    website = models.URLField(unique=True, blank=True, null=True)
    enabled = models.BooleanField(default=True)
    objects = CompanyManager()

    @staticmethod
    def has_read_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group = request.user.groups.filter(Q(name="Manager") |
                                           Q(name="Security Boss"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
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
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        if group and user_company == parameters[0]:
            return True
        return False

    class Meta:
        verbose_name_plural = "Companies"

class UserPermissions(User):
    class Meta:
        proxy = True

    @staticmethod
    def has_read_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group = request.user.groups.filter(Q(name="Manager") |
                                           Q(name="Security Boss"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        print(request.user.customuser.seat_set)
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0]
                and user_seat == parameters[1]):
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
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0]
                and user_seat == parameters[1]):
            return True
        return False


class Company(models.Model):
    """Almacena datos generales de una empresa.
    """
    nit = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, unique=True)
    enabled = models.BooleanField(default=True)
    objects = SeatManager()

    @staticmethod
    def has_read_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group = request.user.groups.filter(Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0]
                and user_seat == parameters[1]):
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
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0]
                and user_seat == parameters[1]):
            return True
        return False

    def __str__(self):
        return self.name


class CustomUser(models.Model):
    """
    Usuario extendido del user de django
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dni = models.CharField(max_length=30, unique=True)
    enabled = models.BooleanField(default=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    # seat = models.ManyToManyField(Seat,
    #                                through='SeatHasUser',
    #                                through_fields=('user',
    #                                                'seat'),
    #                                blank=True)
    objects = CustomUserManager()

    def __str__(self):
        return '{0}: {1} {2}'.format(self.user.first_name,
                                     self.user.last_name,
                                     self.dni)

    @staticmethod
    def has_read_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group = request.user.groups.filter(Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0]
                and user_seat == parameters[1]):
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
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0]
                and user_seat == parameters[1]):
            return True
        return False


class SeatHasUser(models.Model):
    """Tabla intermedia entre usuarios y sedes
    """
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    user = models.OneToOneField(CustomUser,
                                on_delete=models.CASCADE,
                                unique=True)

    class Meta:
        verbose_name_plural = "SeatsHaveUsers"

    def __str__(self):
        return "{0} : {1}".format(str(self.seat).capitalize(),
                                  str(self.user).capitalize())


class Visitor(models.Model):
    """
    Persona que visita la sede de la compañia y trae consigo un
    objeto que se registra
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dni = models.CharField(max_length=30, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    objects = VisitorManager()

    def has_read_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group_limit = request.user.groups.filter(Q(name="Visitor"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        if not group_limit and user_company == parameters[0]:
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
        group_limit = request.user.groups.filter(Q(name="Visitor"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        if not group_limit and user_company == parameters[0]:
            return True
        return False

    def __str__(self):
        return '{0}: {1} {2}'.format(self.first_name,
                                     self.last_name,
                                     self.dni)
