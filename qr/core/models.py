from django.db import models
from django.contrib.auth.models import User
from ubication.models import Location
from items.models import Item
from django.utils import timezone


GENDER_CHOICE = (
    ('M', 'Masculino'),
    ('F', 'Femenino'))


class CustomUser(models.Model):
    """Usuario extendido del user de django

    Atributos:
    preferencial (bool): se usa para hacer descuentos a este usuario
    """
    gender = models.CharField(max_length=2, choices=GENDER_CHOICE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dni = models.CharField(max_length=30)

    def __str__(self):
        return '{0}: {1} {2}'.format(self.user.first_name,
                                     self.user.last_name,
                                     self.dni)


class Company(models.Model):
    """Almacena datos generales de una empresa.
    """
    nit = models.CharField(max_length=15)
    email = models.EmailField()
    name = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    enabled = models.BooleanField(default=True)

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
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Checkin(models.Model):
    item = models.ForeignKey(Item)
    seat = models.ForeignKey(Seat)
    date = models.DateTimeField(default=timezone.now, blank=False)
