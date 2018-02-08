from rest_framework import serializers
from .models import Country, Region, City, Location
from django.db.models.functions import Lower


class CountrySerializerList(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ('id', 'name', 'vat', 'postalcode')


class CountrySerializerDetail(serializers.ModelSerializer):
    regions = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ('id', 'name', 'postalcode', 'vat', 'regions')

    def get_regions(self, obj):
        query = obj.region_set.all().order_by(Lower('name'))
        return RegionSerializerList(query, many=True).data


class RegionSerializerDetail(serializers.ModelSerializer):
    cities = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ('id', 'name', 'cities')

    def get_cities(self, obj):
        c_qs = City.objects.filter(region=obj).order_by(Lower('name'))
        cities = CitySerializerList(c_qs, many=True).data
        return cities


class RegionSerializerList(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = '__all__'


class CitySerializerList(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = '__all__'


class CitySerializerDetail(serializers.ModelSerializer):
    locations = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ('id', 'name', 'locations')

    def get_locations(self, obj):
        query = Location.objects.filter(city=obj)
        location = LocationSerializerDetail(query, many=True).data
        return location


class LocationSerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'address', 'latitude', 'longitude')
