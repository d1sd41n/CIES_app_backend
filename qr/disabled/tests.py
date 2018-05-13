from rest_framework.test import APITestCase
from django.test import tag
import disabled


@tag('TestCreateDisabled')
class TestCreateDisabled(APITestCase):
    def test_create_disabled(self):
        disabled_mockup = disabled.models.Disabled.objects.mockup()
        print("Disabled model test was correct")
        return disabled_mockup
