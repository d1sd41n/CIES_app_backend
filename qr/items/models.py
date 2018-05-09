from .managers import (TypeItemManager,
                       BrandManager,
                       ItemManager,
                       CheckinManager,
                       LostItemManager
                       )
from codes.models import Code
from core.models import Seat, Company, Visitor
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone


class TypeItem(models.Model):
    kind = models.CharField(max_length=30, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                null=True)
    enabled = models.BooleanField(default=True)
    objects = TypeItemManager()

    @staticmethod
    def has_read_permission(request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        if group and user_company == parameters[0]:
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
        if group and user_company == parameters[0]:
            return True
        return False

    def __str__(self):
        return self.kind


class Brand(models.Model):
    brand = models.CharField(max_length=30, unique=True)
    type_item = models.ForeignKey(TypeItem, on_delete=models.CASCADE,
                                  null=True, blank=True)
    enabled = models.BooleanField(default=True)
    objects = BrandManager()

    @staticmethod
    def has_read_permission(request):
        group_limit = request.user.groups.filter(Q(name="Visitor"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        if not group_limit and user_company == parameters[0]:
            return True
        return False

    def has_object_read_permission(self, request):
        group_limit = request.user.groups.filter(Q(name="Visitor"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        if not group_limit and user_company == parameters[0]:
            return True
        return False

    def has_object_write_permission(self, request):
        group_limit = request.user.groups.filter(Q(name="Visitor"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        if not group_limit and user_company == parameters[0]:
            return True
        return False

    @staticmethod
    def has_write_permission(request):
        group_limit = request.user.groups.filter(Q(name="Visitor"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        if not group_limit and user_company == parameters[0]:
            return True
        return False

    def __str__(self):
        return self.brand


class Item(models.Model):
    type_item = models.ForeignKey(TypeItem, on_delete=models.CASCADE)
    code = models.OneToOneField(Code, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE,
                              null=True, blank=True)
    reference = models.CharField(max_length=30, blank=True)
    color = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=255, blank=True)
    lost = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    seat_registration = models.ForeignKey(Seat, on_delete=models.CASCADE,
                                          null=True)
    registration_date = models.DateTimeField(auto_now_add=True, blank=True)
    registered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    objects = ItemManager()

    @staticmethod
    def has_read_permission(request):
        group_limit = request.user.groups.filter(Q(name="Visitor"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        if (not group_limit and user_company == parameters[0]):
            return True
        return False

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        return True

    @staticmethod
    def has_write_permission(request):
        group_limit = request.user.groups.filter(Q(name="Visitor"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        if (not group_limit and user_company == parameters[0]):
            return True
        return False

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
    email = models.EmailField(unique=True, blank=True, null=True)
    visitor_phone = models.CharField(unique=True, max_length=20,
                                     blank=True, null=True)
    closed_case = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    objects = LostItemManager()

    @staticmethod
    def has_read_permission(request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0] and
                user_seat == parameters[1]):
            return True
        return False

    def has_object_read_permission(self, request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0] and
                user_seat == parameters[1]):
            return True
        return False

    def has_object_write_permission(self, request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0] and
                user_seat == parameters[1]):
            return True
        return False

    @staticmethod
    def has_write_permission(request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0] and
                user_seat == parameters[1]):
            return True
        return False

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

    @staticmethod
    def has_read_permission(request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0] and
                user_seat == parameters[1]):
            return True
        return False

    def has_object_read_permission(self, request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0] and
                user_seat == parameters[1]):
            return True
        return False

    def has_object_write_permission(self, request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0] and
                user_seat == parameters[1]):
            return True
        return False

    @staticmethod
    def has_write_permission(request):
        group = request.user.groups.filter(Q(name="Developer") |
                                           Q(name="Manager"))
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        user_seat = str(request.user.customuser.seathasuser.seat_id)
        if (group and user_company == parameters[0] and
                user_seat == parameters[1]):
            return True
        return False

    def __str__(self):
        return self.item
