from rest_framework.test import APITestCase
from django.test import tag
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
    def test_create_product_kind(self):
        item = items.models.Item.objects.mockup()
        print("Brand model test was correct")
        return item


@tag('TestLostItem')
class TestLostItem(APITestCase):
    def test_create_product_kind(self):
        chekin = items.models.LostItem.objects.mockup()
        print("TestLostItem model test was correct")
        return chekin
