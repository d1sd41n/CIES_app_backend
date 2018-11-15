from rest_framework.test import APITestCase
from django.test import tag
from rest_framework import status
import core
from django.contrib.auth.models import User
from core.serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.test import force_authenticate
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from random import randint
from core.models import (Visitor,
                         CustomUser
                        )

@tag('TestVisitor')
class TestVisitor(APITestCase):
    """Esta clase testea la creacion y la view de un visitante
       Ejemplo de ejecusion: 'manage.py test --tag=TestVisitor' """

    def setUp(self):
        print("\n#############################")
        print("####Starting Visitor Test####")
        print("#############################\n")
        self.serializer_attributes = core.models.Visitor.objects.mockup(api=True)
        self.serializer = core.serializers.VisitorSerializer(instance=self.serializer_attributes)
        self.client = APIClient()
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')
        self.token = Token.objects.get(user=self.user)
        group = Group.objects.create(name="Developer")
        group.user_set.add(self.user)

    def test_create_visitor(self):
        print("---starting Visitor create Test---")
        visitor = core.managers.VisitorManager().mockup()
        print("---Visitor model test was correct---")
        return visitor

    def test_visitor_api(self):
        print("---starting Visitor Test api---")
        url = '/core/companies/' + str(self.serializer_attributes['company'].id) + '/visitors/'
        data = self.serializer.data
        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION='Token {}'.format(self.token))

        print("   1.Testing POST response status_code:")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("   ->POST response status_code was correct\n")

        print("   2.Testing the saved data:")
        id = response.data["id"]
        visitor = Visitor.objects.get(id=id).__dict__
        visitor["company"] = visitor.pop("company_id")
        for key in list(data.keys()):
            self.assertEqual(data[key], visitor[key])
        print("   ->saved data were correct\n")

        print("   3.Testing GET response status_code:")
        url = '/core/companies/' + str(self.serializer_attributes['company'].id) + '/visitors/'+str(id)+"/"
        response = self.client.get(url, data, format='json', HTTP_AUTHORIZATION='Token {}'.format(self.token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("   ->Testing GET response status_code were correct\n")

        print("   4.Testing GET response's data:")
        visitor = response.data
        for key in list(data.keys()):
            self.assertEqual(data[key], visitor[key])
        print("   ->GET response's data were correct\n")

        print("   5.Testing PUT response status_code:")
        data["email"] = 'Email'+str(randint(100, 999))+'@test.com'
        response = self.client.put(url, data, format='json', HTTP_AUTHORIZATION='Token {}'.format(self.token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("   ->Testing PUT response status_code were correct\n")

        print("   6.Testing the new visitor's data:")
        visitor = Visitor.objects.get(id=id).__dict__
        visitor["company"] = visitor.pop("company_id")
        for key in list(data.keys()):
            self.assertEqual(data[key], visitor[key])
        print("   ->saved data were correct\n")

        print("---Visitors serializer and API tests were correct---")


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
