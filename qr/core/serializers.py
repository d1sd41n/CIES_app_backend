from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from ubication.models import Location
from core.models import (
    Company,
    Seat,
    CustomUser,
    Visitor,
)


class VisitorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Visitor
        fields = ('__all__')

        extra_kwargs = {
            'company': {'write_only': True},
            'enabled': {'write_only': True},
            }


class CompanySerializerList(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ('id', 'nit', 'name', 'email', 'website')

    def get_seats(self, obj):
        c_qs = Seat.objects.filter(company=obj).order_by(Lower('name'))
        seats = SeatSerializerList(c_qs, many=True).data
        return seats


class SeatSerializerList(serializers.ModelSerializer):

    class Meta:
        model = Seat
        fields = ('id',
                  'name',
                  'address',
                  'email',
                  'company',
                  'enabled')

        extra_kwargs = {
            'company': {'write_only': True},
            }


class SeatSerializerDetail(serializers.ModelSerializer):

    class Meta:
        model = Seat
        fields = '__all__'


class UserSerializerList(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'last_login',
            'is_superuser',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_active',
            'date_joined',
            'password',
            )
        extra_kwargs = {
            'password': {'write_only': True},
            'last_login': {'read_only': True},
            'date_joined': {'read_only': True},
            'id': {'read_only': True},
            }


class UserSerializerDetail(serializers.ModelSerializer):
    """Lista el usuario espesificado de la sede,
    solo muestra los datos de User, no se muestran los de CustomUser,
    Y desde aqui solo se editan los datos de user"""

    class Meta:
        model = User
        fields = (
            'id',
            'last_login',
            'is_superuser',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_active',
            'date_joined',
            )
        extra_kwargs = {
            'username': {'read_only': True},
            'last_login': {'read_only': True},
            'date_joined': {'read_only': True},
            }


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'gender',
            'preferencial',
            'nit',
            'dni',
        )


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'gender',
            'dni',
        )


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
