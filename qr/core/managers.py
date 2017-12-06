from django.db import models
from random import randint
from ubication.models import Location
from django.contrib.auth.models import User
import core


class CompanyManager(models.Manager):
    def mockup(self, api=False):
        data = {'id': None, 'enabled': True, 'nit': randint(111111, 999999),
                'email': "company" + str(randint(1, 100)) + "@" +
                "company" + str(randint(1, 100)) + ".com",
                'name': "company" + str(randint(1, 100))}
        if api:
            return data
        data['website'] = "http://www.company" + str(randint(1, 100)) + ".com"
        return self.create_company(data)

    def create_company(self, data):
        company = self.create(enabled=data['enabled'], nit=data['nit'], email=data['email'], name=data['name'],
                              website=data['website'])
        company.save()
        return company


class SeatManager(models.Manager):
    def mockup(self, api=False):
        data = {'id': None, 'address': Location.objects.mockup(),
                'name': "Seat" + str(randint(1, 99)) + "-seat",
                'company': core.models.Company.objects.mockup(),
                'email': "seat" + str(randint(1, 50)) + "@" +
                "seat" + str(randint(1, 50)) + ".com"}
        if api:
            return data
        return self.create_seat(data)

    def create_seat(self, data):
        seat = self.create(address=data['address'], company=data['company'],
                           email=data['email'],
                           name=data['name'])
        seat.save()
        return seat


class UserManager(models.Manager):
    def mockup(self, api=False):
        selection = {1: True, 2: False}
        gender_selection = {1: 'F', 2: 'M'}
        data = {'id': None, 'username': "usuario" + str(123),
                'first_name': "Usuario" + str(randint(1, 9999)),
                'last_name': "Apellido" + str(randint(1, 9999)),
                'is_active': selection[randint(1, 2)],
                'is_superuser': selection[randint(1, 2)],
                'is_staff': selection[randint(1, 2)],
                'password': "AdiVIne" + str(randint(111111, 999999999)),
                'gender': gender_selection[randint(1, 2)],
                'preferencial': selection[randint(1, 2)],
                'last_login': None,
                'dni': randint(11111, 99999),
                'email': "Usuario" + str(randint(1, 9999)) + "@" + "email" + ".com"}
        if api:
            return data
        return self.create_user(data)

    def create_user(self, data):
        user = User.objects.create(username=data['first_name'] + str(123),
                                   is_superuser=data['is_superuser'], is_staff=data['is_staff'],
                                   is_active=data['is_active'],
                                   first_name=data['first_name'],
                                   last_name=data['last_name'],
                                   email=data['email'],
                                   password=data['password'])
        user.save()
        customUser = core.models.CustomUser.objects.create(
                                 gender=data['gender'],
                                 user=user,
                                 dni=data['dni'],
                                 )
        customUser.save()
        return customUser
