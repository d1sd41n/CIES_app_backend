from rest_framework import serializers
from django.db.models.functions import Lower
from ubication.models import Location
from django.contrib.auth.models import User
from core.models import (
    Company,
    Seat,
    UserPermissions,
    CustomUser,
    Visitor,
)


class VisitorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Visitor
        fields = ('__all__')
        read_only_fields = ('enabled',)


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ('id', 'nit', 'name', 'email', 'website')
        extra_kwargs = {'enabled': {'read_only': True}}


class SeatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Seat
        fields = '__all__'
        extra_kwargs = {'enabled': {'read_only': True}}

class SeatSerializerList(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    address = serializers.CharField()
    company = serializers.CharField()
    email = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User#UserPermissions
        fields = '__all__'
        read_only_fields = ('date_joined', 'last_login', 'enabled')


class UserSerializerListCustom(serializers.Serializer):
    id = serializers.IntegerField()
    last_login = serializers.DateTimeField()
    username = serializers.CharField(max_length=100)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    date_joined = serializers.DateTimeField()
    dni = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=100)
    type = serializers.CharField(max_length=10)


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {'enabled': {'read_only': True}}


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        extra_kwargs = {'enabled': {'read_only': True}}
