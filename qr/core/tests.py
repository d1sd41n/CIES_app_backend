from rest_framework.test import APITestCase
from django.test import tag
from rest_framework import status
import core
from core.models import CustomUser
from core.serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404

@tag('TestVisitor')
class TestVisitor(APITestCase):
    """Esta clase testea la creacion y la view de un visitante"""

    def setUp(self):
        print("starting Visitor Test")
        self.serializer_attributes = core.models.Visitor.objects.mockup(api=True)
        self.serializer = core.serializers.VisitorSerializer(instance=self.serializer_attributes)

    def test_create_visitor(self):
        print("starting Visitor create Test")
        visitor = core.managers.VisitorManager().mockup()
        print("Visitor model test was correct")
        return visitor

    def test_create_visitor_api(self):
        print("starting Visitor Test api")
        url = '/core/companies/' + str(self.serializer_attributes['company'].id) + '/visitors/'
        data = self.serializer.data
        response = self.client.post(url, data, format='json')
        data['id'] = response.data['id']
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("Visitors serializer and API tests were correct")


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
        print("starting create user test")
        seat = core.models.Seat.objects.mockup()
        print("Seat model test was correct.")
        return seat


@tag('TestUser')
class TestUser(APITestCase):
    """Esta clase testea la creacion de un usuario"""

    def setUp(self):
        print("starting user test")
        self.serializer_attributes = core.managers.UserManager().mockup(api=True)
        return self.serializer_attributes

    def test_create_user(self):
        user = core.managers.UserManager().mockup()
        print("User model test was correct")
        return user

    def test_create_user_api(self):
        print("Testing Seat User")
        seat = core.models.Seat.objects.mockup()
        url = '/core/companies/' + str(seat.company.id) + '/seats/' + str(seat.id) + '/users/'
        data = self.setUp()
        response = self.client.post(url, data, format='json')
        data['id'] = response.data['id']
        data['last_login'] = response.data['last_login']
        data['date_joined'] = response.data['date_joined']
        serializer = core.serializers.UserSerializerList(instance=data).data
        self.assertEqual(response.data, serializer)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("User serializer and API tests were correct")
        custom = get_object_or_404(
                    CustomUser,
                    user=response.data['id']
                    )
        serializerCustomFromDB = CustomUserSerializer(custom)
        serializerCustomFromData = CustomUserSerializer(instance=data)
        self.assertEqual(serializerCustomFromDB.data,
                         serializerCustomFromData.data)
        self.assertEqual(set(serializerCustomFromDB.data.keys()),
                         set(serializerCustomFromData.data.keys()))
        print("CustomUser serializer and API tests were correct")
