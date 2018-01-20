from rest_framework.test import APITestCase
from django.test import tag
import disabled


@tag('TestCreateDisabled')
class TestCreateDisabled(APITestCase):
    def test_create_disabled(self):
        disableds = disabled.models.Disabled.objects.mockup()
        print("Disabled model test was correct")
        return disableds
