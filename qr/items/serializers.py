from rest_framework import serializers
from items.models import (
        Item,
        Checkin
)

class ItemSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=30)
    color = serializers.CharField(max_length=30)
    description = serializers.CharField(max_length=255)
    lost = serializers.BooleanField(default=False)
    type_item = serializers.CharField(max_length=30)
    owner_name = serializers.CharField(max_length=50)
    owner_last_name = serializers.CharField(max_length=50)
    owner_dni = serializers.CharField(max_length=30)
    brand = serializers.CharField(max_length=30)
    registered_in = serializers.CharField(max_length=100)


class ChekinSerializer(serializers.ModelSerializer):

    class Meta:
        model = Checkin
        fields = ('__all__')

        # extra_kwargs = {
        #     'company': {'write_only': True},
        #     'enabled': {'write_only': True},
            # }
