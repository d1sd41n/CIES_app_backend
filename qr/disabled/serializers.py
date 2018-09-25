from rest_framework import serializers

from disabled.models import Disabled


class DisabledModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disabled
        fields = ('__all__')
        extra_kwargs = {'enabled': {'read_only': True}}
