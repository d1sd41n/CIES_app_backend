from rest_framework.test import APITestCase
from django.test import tag
from .models import *
# python manage.py test --tag=TestRegion


@tag('TestCountry')
class TestCountry(APITestCase):
    def test_create_country(self):
        country = Country.objects.mockup()
        print("Country model test was correct")
        return country


@tag('TestRegion')
class TestRegion(APITestCase):
    def test_create_region(self):
        region = Region.objects.mockup()
        print("Region model test was correct")
        return region
        print("Region serializer and API tests were correct")


@tag('TestCity')
class TestCity(APITestCase):
    def test_create_city(self):
        city = City.objects.mockup()
        print("City model test was correct")
        return city


@tag('TestLocation')
class TestLocation(APITestCase):
    def test_create_location(self):
        location = Location.objects.mockup()
        print("Location model test was correct")
        return location
