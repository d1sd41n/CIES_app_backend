from rest_framework import serializers
from codes.models import Code


class CodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code
        fields = '__all__'
