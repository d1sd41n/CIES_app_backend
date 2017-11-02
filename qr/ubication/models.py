from django.db import models


class Country(models.Model):
    """se almacena el pais de ubicacion"""
    name = models.CharField(max_length=50)
    postalcode = models.CharField(max_length=3, null=True, blank=True)
    vat = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class Region(models.Model):
    """Se almacena el estado, departamento o region
    """
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class City(models.Model):
    """Se almacena ciudades o municipios
    """
    name = models.CharField(max_length=50)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name


class Location(models.Model):
    """Almacena la latitud y longitud de algun objeto
    """
    address = models.CharField(max_length=100)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return self.address+" "+str(self.city).capitalize()
