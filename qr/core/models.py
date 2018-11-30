from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from core.managers import (CompanyManager, CustomUserManager, SeatManager,
                           VisitorManager)
from ubication.models import Location


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Company(models.Model):
    """Almacena datos generales de una empresa.
    """
    nit = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, unique=True)
    website = models.URLField(unique=True, blank=True, null=True)
    enabled = models.BooleanField(default=True)
    objects = CompanyManager()

    def has_read_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        return False

    def has_object_read_permission(self, request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        return False

    def has_object_write_permission(self, request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        return False

    def has_write_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        return False

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Seat(models.Model):
    """Almacena diferentes sedes de una compañia
    """
    address = models.OneToOneField(Location, on_delete=models.CASCADE,
                                   blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    name = models.CharField(max_length=100, unique=True)
    enabled = models.BooleanField(default=True)
    phone = models.CharField(max_length=15, unique=True, blank=True)
    objects = SeatManager()

    def has_read_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group = request.user.groups.filter(Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company.id)
        if (group and user_company == parameters[0]):
            return True
        return False

    def has_object_read_permission(self, request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group = request.user.groups.filter(Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company.id)
        user_seat = str(CustomUser.objects.get(user=request.user).seat.id)
        if (group and user_company == parameters[0]
                and user_seat == parameters[1]):
            return True
        return False

    def has_object_write_permission(self, request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group = request.user.groups.filter(Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company.id)
        user_seat = str(CustomUser.objects.get(user=request.user).seat.id)
        if (group and user_company == parameters[0]
                and user_seat == parameters[1]):
            return True
        return False

    def has_write_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group = request.user.groups.filter(Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company.id)
        if (group and user_company == parameters[0]):
            return True
        return False

    def __str__(self):
        return self.name


class CustomUser(models.Model):
    """
    Usuario extendido del user de django
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    dni = models.CharField(max_length=30, unique=True)
    enabled = models.BooleanField(default=True)
    objects = CustomUserManager()

    def __str__(self):
        return '{0} - {1}: {2} {3}'.format(self.user.username,
                                           self.user.first_name,
                                           self.user.last_name,
                                           self.dni)

    @staticmethod
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
        user_seat = str(CustomUser.objects.get(user=request.user).seat.id)
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
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company.id)
        user_seat = str(CustomUser.objects.get(user=request.user).seat.id)
        if (group and user_company == parameters[0]
                and user_seat == parameters[1]):
            return True
        return False


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
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company.id)
        user_seat = str(CustomUser.objects.get(user=request.user).seat.id)
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
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company.id)
        user_seat = str(CustomUser.objects.get(user=request.user).seat.id)
        if (group and user_company == parameters[0]
                and user_seat == parameters[1]):
            return True
        return False


class Visitor(models.Model):
    """
    Persona que visita la sede de la compañia y trae consigo un
    objeto que se registra
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dni = models.CharField(max_length=50, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=10, null=True, blank=True)
    objects = VisitorManager()

    def has_read_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group_limit = request.user.groups.filter(Q(name="Visitor"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company.id)
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
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company.id)
        if not group_limit and user_company == parameters[0]:
            return True
        return False

    def __str__(self):
        return '{0}: {1} {2}'.format(self.first_name,
                                     self.last_name,
                                     self.dni)
