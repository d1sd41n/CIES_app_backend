from django.db import models
from django.db.models import Q

from core.models import Company, CustomUser

from .managers import (CityManager, CountryManager, LocationManager,
                       RegionManager)


class Country(models.Model):
    """se almacena el pais de ubicacion"""
    name = models.CharField(max_length=50, unique=True)
    postalcode = models.CharField(unique=True, max_length=15,
                                  null=True, blank=True)
    objects = CountryManager()

    @staticmethod
    def has_read_permission(request):
        group = request.user.groups.filter(Q(name="Developer"))
        if group:
            return True
        return False

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        return True

    @staticmethod
    def has_write_permission(request):
        group = request.user.groups.filter(Q(name="Developer"))
        if group:
            return True
        return False

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class Province(models.Model):
    """Se almacena el estado, departamento o region
    """
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    objects = RegionManager()

    @staticmethod
    def has_read_permission(request):
        group = request.user.groups.filter(Q(name="Developer"))
        if group:
            return True
        return False

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        return True

    @staticmethod
    def has_write_permission(request):
        group = request.user.groups.filter(Q(name="Developer"))
        if group:
            return True
        return False

    def __str__(self):
        return self.name


class City(models.Model):
    """Se almacena ciudades o municipios
    """
    name = models.CharField(max_length=50)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    objects = CityManager()

    @staticmethod
    def has_read_permission(request):
        group = request.user.groups.filter(Q(name="Developer"))
        if group:
            return True
        return False

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        return True

    @staticmethod
    def has_write_permission(request):
        group = request.user.groups.filter(Q(name="Developer"))
        if group:
            return True
        return False

    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name


class Location(models.Model):
    """Almacena la latitud y longitud de algun objeto
    """
    address = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    objects = LocationManager()

    @staticmethod
    def has_read_permission(request):
        developer_permission = request.user.groups.filter(Q(name="Developer"))
        if developer_permission:
            return True
        group = request.user.groups.filter(Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company)
        user_seat = str(CustomUser.objects.get(user=request.user).seat)
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
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company)
        user_seat = str(CustomUser.objects.get(user=request.user).seat)
        if (group and user_company == parameters[0]
                and user_seat == parameters[1]):
            return True
        return False

    def __str__(self):
        return self.address + " " + str(self.city).capitalize()
