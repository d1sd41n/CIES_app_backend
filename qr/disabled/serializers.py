from rest_framework import serializers
from disabled.models import Disabled


class DisabledModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disabled
        fields = ('__all__')
        extra_kwargs = {
            'id': {'read_only': True},
            'company': {'write_only': True},
            }
