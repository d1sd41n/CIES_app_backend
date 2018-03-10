from django.db import models
from core.models import Seat, Company
from random import randint
import items
import core
import codes


class TypeItemManager(models.Manager):
    def mockup(self, api=False):
        data = {'id': None, 'kind': "Tipo item" + str(randint(1, 100)),
                'company': Company.objects.mockup()}
        if api:
            return data
        return self.create_item_kind(data)

    def create_item_kind(self, data):
        type_item = self.create(kind=data['kind'], company=data['company'])
        type_item.save()
        return type_item


class BrandManager(models.Manager):
    def mockup(self, api=False):
        data = {'id': None, 'brand': "marca" + str(randint(1, 100)),
                'type_item': items.models.TypeItem.objects.mockup()}
        if api:
            return data
        return self.create_brand(data)

    def create_brand(self, data):
        brand = self.create(brand=data['brand'], type_item=data['type_item'])
        brand.save()
        return brand


class ItemManager(models.Manager):
    def mockup(self, api=False):
        item_type = items.models.TypeItem.objects.mockup()
        visitor = core.managers.VisitorManager().mockup()
        brand = items.models.Brand.objects.mockup()
        registeredBy = core.managers.UserManager().mockup()
        seatRegistration = Seat.objects.mockup()
        # code = codes.managers.CodeManager().mockup()
        data = {'id': None, 'color': "color" + str(randint(1, 100)),
                'reference': str(randint(1, 100)),
                'description': "ssdadadf",
                'type_item': item_type,
                'brand': brand,
                'owner': visitor,
                'registeredBy': registeredBy,
                'seatRegistration': seatRegistration,
                # 'code': code
                }
        if api:
            return data
        return self.create_item(data)

    def create_item(self, data):
        item = self.create(color=data['color'],
                           reference=data['reference'],
                           description=data['description'],
                           type_item=data['type_item'],
                           brand=data['brand'],
                           owner=data['owner'],
                           registeredBy=data['registeredBy'],
                           seatRegistration=data['seatRegistration'],
                           code=None
                           )
        item.save()
        return item


class CheckinManager(models.Manager):
    def mockup(self, api=False):
        item = items.models.Item.objects.mockup()
        data = {'id': None,
                'item': item,
                'go_in': True,
                'seat':  Seat.objects.mockup()}
        if api:
            return data
        return self.create_chekin(data)

    def create_chekin(self, data):
        chekin = self.create(item=data['item'],
                             go_in=data['go_in'],
                             seat=data['seat'])
        chekin.save()
        return chekin


class LostItemManager(models.Manager):
    def mockup(self, api=False):
        item = items.models.Item.objects.mockup()
        data = {'id': None,
                'item': item,
                'date': "2017-09-15T01:03:00",
                'description':  "ddssdasdas"}
        if api:
            return data
        return self.create_lost_item(data)

    def create_lost_item(self, data):
        l_item = self.create(item=data['item'],
                             date=data['date'],
                             description=data['description'])
        l_item.save()
        return l_item
