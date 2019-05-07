from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone

from codes.models import Code
from core.models import Company, CustomUser, Seat, Visitor

from .managers import (BrandManager, CheckinManager, ItemManager,
                       LostItemManager, TypeItemManager)


class TypeItem(models.Model):
    kind = models.CharField(max_length=30)
    company = models.ForeignKey(Company, blank=True, null=True)
    enabled = models.BooleanField(default=True)
    objects = TypeItemManager()

    def __str__(self):
        return self.kind


class Brand(models.Model):
    brand = models.CharField(max_length=30)
    type_item = models.ForeignKey(TypeItem, on_delete=models.CASCADE,
                                  null=True, blank=True)
    enabled = models.BooleanField(default=True)
    objects = BrandManager()

    def __str__(self):
        return self.brand


class Item(models.Model):
    type_item = models.ForeignKey(
        TypeItem, on_delete=models.CASCADE)
    code = models.OneToOneField(Code, on_delete=models.CASCADE)
    owner = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE,
                              null=True, blank=True)
    reference = models.CharField(max_length=30, blank=True)
    color = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=255, blank=True)
    lost = models.BooleanField(default=False)
    lost_date = models.DateTimeField(null=True, blank=True)
    enabled = models.BooleanField(default=True)
    seat_registration = models.ForeignKey(Seat, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True, blank=True)
    registered_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                      blank=True, null=True)
    objects = ItemManager()

    def __str__(self):
        return '{0} : {1} : {2}'.format(self.owner,
                                        self.reference,
                                        self.type_item)


class LostItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now=True, blank=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, blank=True,
                             null=True)
    closed_case = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    objects = LostItemManager()

    def __str__(self):
        return self.item.type_item.kind


class CheckIn(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    worker = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                               blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True)
    go_in = models.BooleanField()
    objects = CheckinManager()

    def __str__(self):
        return str(self.item)
