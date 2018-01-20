from rest_framework.test import APITestCase
from django.test import tag
from codes.models import Code


@tag('TestCode')
class TestCode(APITestCase):
    def test_create_type_item(self):
        code = Code.objects.mockup()
        print("Code model test was correct")
        return code
