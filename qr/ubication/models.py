from django.db import models
from django.db.models import Q

from .managers import (CityManager, CountryManager, LocationManager,
                       RegionManager)


class Country(models.Model):
    """se almacena el pais de ubicacion"""
    name = models.CharField(max_length=50, unique=True)
    postalcode = models.CharField(unique=True, max_length=15,
                                  null=True, blank=True)
    objects = CountryManager()

    def __str__(self):
        return self.name


class Province(models.Model):
    """Se almacena el estado, departamento o region
    """
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    objects = RegionManager()

    def __str__(self):
        return self.name


class City(models.Model):
    """Se almacena ciudades o municipios
    """
    name = models.CharField(max_length=50)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    objects = CityManager()

    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name


class Location(models.Model):
    """Almacena la latitud y longitud de algun objeto
    """
    address = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    objects = LocationManager()

    def __str__(self):
        return self.address + " " + str(self.city).capitalize()
