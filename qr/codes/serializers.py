from rest_framework import serializers

from codes.models import Code


class CodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code
        fields = ('__all__')
        extra_kwargs = {'enabled': {'read_only': True}}


class GenerateCodesSerializer(serializers.Serializer):
    pages = serializers.IntegerField()

    def create(self, validated_data):
        return validated_data

    # class Meta:
    #     model = Code
    #     fields = ('__all__')
    #     extra_kwargs = {'enabled': {'read_only': True},
    #                     'used': {'read_only': True},
    #                     'seat': {'read_only': True}}
