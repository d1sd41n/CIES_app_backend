from django.db import models
from django.contrib.auth.models import User
from ubication.models import Location
from core.managers import (
                            CustomUserManager,
                            CompanyManager,
                            SeatManager,
                            )


GENDER_CHOICE = (
    ('M', 'Masculino'),
    ('F', 'Femenino'))


class CustomUser(models.Model):
    """Usuario extendido del user de django

    Atributos:
    preferencial (bool): se usa para hacer descuentos a este usuario
    """
    address = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True,
                                null=True)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dni = models.CharField(max_length=30, unique=True)
    enabled = models.BooleanField(default=True)
    objects = CustomUserManager()

    def __str__(self):
        return '{0}: {1} {2}'.format(self.user.first_name,
                                     self.user.last_name,
                                     self.dni)


class Company(models.Model):
    """Almacena datos generales de una empresa.
    """
    nit = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    enabled = models.BooleanField(default=True)
    objects = CompanyManager()

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
    users = models.ManyToManyField(CustomUser,
                                   through='SeatHasUser',
                                   through_fields=('seat',
                                                   'user'))
    objects = SeatManager()

    def __str__(self):
        return self.name


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
    """Persona que visita la sede de la compañia y trae consigo un
    objeto que se registra
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICE)
    dni = models.CharField(max_length=30, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return '{0}: {1} {2}'.format(self.first_name,
                                     self.last_name,
                                     self.dni)
