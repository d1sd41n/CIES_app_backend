from django.db import models
from random import randint
import ubication


class CountryManager(models.Manager):
    def mockup(self, api=False):
        data = {'id': None, 'name': "Country"+str(randint(1, 99)),
                'postalcode': str(randint(100, 999)),
                'vat': float(randint(1, 20))}
        if api:
            return data
        return self.create_country(data)

    def create_country(self, data):
        country = self.create(name=data['name'], postalcode=data['postalcode'],
                              vat=data['vat'])
        country.save()
        return country


class RegionManager(models.Manager):
    def mockup(self, api=False):
        data = {'id': None, 'name': "Region"+str(randint(1, 99)),
                'country': ubication.models.Country.objects.mockup()}
        if api:
            return data
        return self.create_region(data)

    def create_region(self, data):
        region = self.create(name=data['name'], country=data['country'])
        region.save()
        return region


class CityManager(models.Manager):
    def mockup(self, api=False):
        data = {'id': None, 'name': "City" + str(randint(1, 99)),
                'region': ubication.models.Region.objects.mockup()}
        if api:
            return data
        return self.create_city(data)

    def create_city(self, data):
        city = self.create(name=data['name'], region=data['region'])
        city.save()
        return city


class LocationManager(models.Manager):
    def mockup(self, api=False):
        data = {'id': None, 'address': "Carrera" + str(randint(1, 99)),
                'latitude': float(randint(1, 99)),
                'longitude': float(randint(1, 99)),
                'city': ubication.models.City.objects.mockup()}
        if api:
            return data
        return self.create_location(data)

    def create_location(self, data):
        location = self.create(address=data['address'],
                               latitude=data['latitude'],
                               longitude=data['longitude'],
                               city=data['city'])
        location.save()
        return location
