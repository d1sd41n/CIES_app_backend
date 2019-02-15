from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import CustomUser
from disabled.models import Disabled
from disabled.serializers import DisabledModelSerializer
from items.models import Brand, Item, LostItem, TypeItem
from django.contrib.contenttypes.models import ContentType
from qr.permissions import ManagerAndSuperiorsOnly


class DisableModelsViewSet(APIView):
    """
    URL de este endpoint :  http://localhost:8000/disabled/companies/pk/seats/pk/disabled-models/
    En este EndPoint se desactivan datos pertenecientes a
    una compañía.

    El JSON se debe escribir de la siguiente manera:

    {
    "pk_object": 1,
    "model": "item"
    }

    lista de modelos:
    "item",
    "user"

    Por ahora solo estarán esos dos tipos de modelos, posiblemente en el futuro
    se agregarán mas.
    """
    queryset = Disabled.objects.all()
    permission_classes = [ManagerAndSuperiorsOnly]

    def post(self, request, company_pk, seat_pk):
        model = request.data['model']
        object_id = request.data['pk_object']
        if model in ["brand", "user", "typeitem", "item"]:
            object_type = ContentType.objects.get(model=model)
            object = object_type.get_object_for_this_type(id=object_id)

            if model == "item":
                if object.type_item.company.id != int(company_pk):
                    return Response({"Response": "Usted no tiene permiso para realizar esta accion"},status=status.HTTP_403_FORBIDDEN)
            elif model == "user":
                custom_user = CustomUser.objects.get(user=object_id)
                sea_user_id = custom_user.seat.id
                company_user_id = custom_user.seat.company.id
                if company_user_id != int(company_pk) or sea_user_id != int(seat_pk) or "Manager" in object.groups.values_list('name',flat=True):
                    return Response({"Response": "Usted no tiene permiso para realizar esta accion"},status=status.HTTP_403_FORBIDDEN)
                object.is_active = False
                object.save()
                return Response({"Response": "Objeto eliminado"}, status=status.HTTP_200_OK)
            object.enabled = False
            object.save()
            return Response({"Response": "Objeto eliminado"}, status=status.HTTP_200_OK)
