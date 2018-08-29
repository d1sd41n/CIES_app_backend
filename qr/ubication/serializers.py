from rest_framework import serializers
from .models import Country, Province, City, Location
from django.db.models.functions import Lower


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ('id', 'name', 'postalcode')


class ProvinceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Province
        fields = '__all__'
        extra_kwargs = {'enabled': {'read_only': True}}


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = '__all__'
        extra_kwargs = {'enabled': {'read_only': True}}
