from django.db import models
from django.contrib.auth.models import User
from core.models import Seat
from django.utils import timezone
from .managers import (TypeItemManager,
                       BrandManager,
                       ItemManager,
                       CheckinManager,
                       LostItemManager
                       )


class TypeItem(models.Model):
    kind = models.CharField(max_length=30)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    objects = TypeItemManager()

    def __str__(self):
        return self.kind


class Brand(models.Model):
    brand = models.CharField(max_length=30)
    type_item = models.ForeignKey(TypeItem, null=True, blank=True)
    enabled = models.BooleanField(default=True)
    objects = BrandManager()

    def __str__(self):
        return self.brand


class Item(models.Model):
    type_item = models.ForeignKey(TypeItem)
    owner = models.ForeignKey(User)
    brand = models.ForeignKey(Brand, null=True, blank=True)
    reference = models.CharField(max_length=30, blank=True)
    color = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=255, blank=True)
    lost = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    objects = ItemManager()

    def __str__(self):
        return '{0} : {1} : {2}'.format(self.owner,
                                        self.reference,
                                        self.type_item)


class LostItem(models.Model):
    item = models.OneToOneField(Item)
    description = models.CharField(max_length=255)
    date = models.DateTimeField()
    objects = LostItemManager()

    def __str__(self):
        return self.item


class Checkin(models.Model):
    item = models.ForeignKey(Item)
    seat = models.ForeignKey(Seat)
    date = models.DateTimeField(default=timezone.now, blank=False)
    go_in = models.BooleanField()
    objects = CheckinManager()
