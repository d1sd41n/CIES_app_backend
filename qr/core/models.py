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
    name = models.CharField(max_length=100)
    website = models.URLField(unique=True, blank=True, null=True)
    enabled = models.BooleanField(default=True)
    objects = CompanyManager()

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name



class Seat(models.Model):
    """Almacena diferentes sedes de una compañia
    """
    address = models.OneToOneField(Location, on_delete=models.SET_NULL,
                                   blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    name = models.CharField(max_length=100, unique=True)
    enabled = models.BooleanField(default=True)
    phone = models.CharField(max_length=15, unique=True, blank=True)
    objects = SeatManager()

    def __str__(self):
        return self.name



class CustomUser(models.Model):
    """
    Usuario extendido del user de django
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    dni = models.CharField(max_length=30, unique=True)
    objects = CustomUserManager()

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return '{0} - {1}: {2} {3}'.format(self.user.username,
                                           self.user.first_name,
                                           self.user.last_name,
                                           self.dni)


class Visitor(models.Model):
    """
    Persona que visita la sede de la compañia y trae consigo un
    objeto que se registra
    """

    class Meta:
        verbose_name = "visitante"
        verbose_name_plural = "visitantes"

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dni = models.CharField(max_length=50, unique=True)
    company = models.ManyToManyField(Company, blank=True)
    enabled = models.BooleanField(default=True)
    email = models.EmailField(null=True, unique=True)
    phone = models.CharField(max_length=10, null=True, blank=True)
    seat_registration = models.ForeignKey(Seat, blank=True, null=True, on_delete=models.SET_NULL)
    registration_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    registered_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    objects = VisitorManager()

    def __str__(self):
        return '{0}: {1} {2}'.format(self.first_name,
                                     self.last_name,
                                     self.dni)


# This makes User's email unique in the DB
from django.contrib.auth.models import User
User._meta.get_field('email')._unique = True
