from rest_framework.test import APITestCase
from django.test import tag
from rest_framework import status
import items


@tag('TestTypeItem')
class TestTypeItem(APITestCase):
    def test_create_type_item(self):
        item_type = items.models.TypeItem.objects.mockup()
        print("TypeItem model test was correct")
        return item_type


@tag('TestBrand')
class TestBrand(APITestCase):
    def test_create_product_kind(self):
        brand = items.models.Brand.objects.mockup()
        print("Brand model test was correct")
        return brand


@tag('TestItem')
class TestItem(APITestCase):

    def setUp(self):
        print("starting item Test")
        self.serializer_attributes = items.models.Item.objects.mockup(api=True)
        self.serializer = items.serializers.RegisterItemTest(instance=self.serializer_attributes)

    def test_create_product_kind(self):
        item = items.models.Item.objects.mockup()
        print("Item model test was correct")
        return item

    def test_create_item_api(self):
        print("starting Item Test api")
        companyid = str(self.serializer_attributes['seatRegistration'].company.id)
        seatid = str(self.serializer_attributes['seatRegistration'].id)
        url = '/items/companies/' + companyid + '/seats/'+ seatid + '/registeritem/'
        data = self.serializer.data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("Visitors serializer and API tests were correct")


@tag('TestLostItem')
class TestLostItem(APITestCase):
    def test_create_product_kind(self):
        chekin = items.models.LostItem.objects.mockup()
        print("TestLostItem model test was correct")
        return chekin
