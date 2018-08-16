from rest_framework import serializers
from django.db.models.functions import Lower
from ubication.models import Location
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


class CompanySerializerList(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ('id', 'nit', 'name', 'email', 'website')
        extra_kwargs = {'enabled': {'read_only': True}}

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

        read_only_fields = ('company', 'enabled')


class SeatSerializerDetail(serializers.ModelSerializer):

    class Meta:
        model = Seat
        fields = '__all__'
        extra_kwargs = {'enabled': {'read_only': True}}


class UserSerializerList(serializers.ModelSerializer):

    class Meta:
        model = UserPermissions
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
        read_only_fields = ('password', 'date_joined', 'last_login', 'enabled')


class UserSerializerListCustom(serializers.Serializer):
    id = serializers.IntegerField()
    last_login = serializers.DateTimeField()
    is_superuser = serializers.BooleanField(default=False)
    username = serializers.CharField(max_length=100)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    is_staff = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=False)
    date_joined = serializers.DateTimeField()
    dni = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=100)


class UserSerializerDetail(serializers.ModelSerializer):
    """Lista el usuario espesificado de la sede,
    solo muestra los datos de User, no se muestran los de CustomUser,
    Y desde aqui solo se editan los datos de user"""

    class Meta:
        model = UserPermissions
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
        read_only_fields = ('username', 'last_login', 'date_joined', 'enabled')


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'dni',
            'enabled',
        )
        extra_kwargs = {'enabled': {'read_only': True}}


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        extra_kwargs = {'enabled': {'read_only': True}}
