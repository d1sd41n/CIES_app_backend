from rest_framework.response import Response
from codes.serializers import CodesSerializer
from codes.models import Code
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404


class GetCode(APIView):
    """muestra un codigo, se debe ingresar la url de la siguiente manera:
    http://localhost:8000/codes/getcode/ff0d0ddb-c055-4824-9844-104e4c94f01d/

    lo que sigue despues de /getcode/ es el hash que se desa buscar"""
    def get(self, request, code, format=None):
        code = get_object_or_404(
               Code,
               code=code,
               )
        serializer = CodesSerializer(code)
        return Response(serializer.data)
