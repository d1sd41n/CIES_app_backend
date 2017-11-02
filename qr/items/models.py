from django.db import models
from django.contrib.auth.models import User


class TypeItem(models.Model):
    kind = models.CharField(max_length=30)

    def __str__(self):
        return self.kind


class Brand(models.Model):
    brand = models.CharField(max_length=30)
    type_item = models.ForeignKey(TypeItem, null=True, blank=True)

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

    def __str__(self):
        return '{0} : {1} : {2}'.format(self.owner,
                                        self.reference,
                                        self.type_item)


class LostItem(models.Model):
    item = models.OneToOneField(Item)
    description = models.CharField(max_length=255)
    date = models.DateTimeField()

    def __str__(self):
        return self.item
