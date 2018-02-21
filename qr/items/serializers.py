from rest_framework import serializers
from items.models import (
        Item,
        Checkin,
        TypeItem,
        Brand,
)

class ItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    reference = serializers.CharField(max_length=30)
    color = serializers.CharField(max_length=30)
    description = serializers.CharField(max_length=255)
    lost = serializers.BooleanField(default=False)
    type_item = serializers.CharField(max_length=30)
    owner_name = serializers.CharField(max_length=50)
    owner_last_name = serializers.CharField(max_length=50)
    owner_dni = serializers.CharField(max_length=30)
    brand = serializers.CharField(max_length=30)
    registered_in_seat = serializers.CharField(max_length=100)
    registered_in_seat_id = serializers.IntegerField()
    company_id = serializers.IntegerField()
    registration_date = serializers.DateField()
    registeredBy = serializers.IntegerField()
    code = serializers.CharField(max_length=35)


class ChekinSerializer(serializers.ModelSerializer):

    class Meta:
        model = Checkin
        fields = ('__all__')

        # extra_kwargs = {
        #     'company': {'write_only': True},
        #     'enabled': {'write_only': True},
            # }


class TypeItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = TypeItem
        fields = ('__all__')


class Branderializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = ('__all__')


class RegisterItem(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('__all__')
