from rest_framework import serializers
from disabled.models import Disabled


class DisabledModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disabled
        fields = ('__all__')
        read_only_fields = ('company', 'enabled')
