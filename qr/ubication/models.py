from .managers import (CountryManager, RegionManager,
                       CityManager, LocationManager)
from django.db import models
from django.db.models import Q


class Country(models.Model):
    """se almacena el pais de ubicacion"""
    name = models.CharField(max_length=50, unique=True)
    postalcode = models.CharField(unique=True, max_length=3,
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


class Region(models.Model):
    """Se almacena el estado, departamento o region
    """
    name = models.CharField(unique=True, max_length=50)
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
    name = models.CharField(unique=True, max_length=50)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
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
    latitude = models.FloatField(unique=True, blank=True, null=True)
    longitude = models.FloatField(unique=True, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    objects = LocationManager()

    @staticmethod
    def has_read_permission(request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager"))
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
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0]
                and user_seat == parameters[1]):
            return True
        return False

    def __str__(self):
        return self.address+" "+str(self.city).capitalize()
