from rest_framework.test import APITestCase
from django.test import tag
import core


@tag('TestCompany')
class TestCompany(APITestCase):
    """Esta clase testea la creacion de una compañia"""

    def test_create_company(self):
        company = core.models.Company.objects.mockup()
        print("Company model test was correct")
        return company


@tag('SeatManager')
class TestSeat(APITestCase):
    """Esta clase testea la creacion de una sede y su direccion"""
    def test_create_seat(self):
        seat = core.models.Seat.objects.mockup()
        print("Seat model test was correct.")
        return seat


@tag('TestUser')
class TestUser(APITestCase):
    """Esta clase testea la creacion de un usuario"""
    def test_create_user(self):
        if core.managers.UserManager().mockup():
            print("User model test was correct")
