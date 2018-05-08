from core.models import Visitor
from disabled.models import Disabled
from disabled.serializers import (
                                  DisabledModelSerializer
                                  )
from django.shortcuts import get_object_or_404
from dry_rest_permissions.generics import DRYPermissions
from items.models import (
                        TypeItem,
                        Brand,
                        Item,
                        LostItem,
                        )
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets


class DisableModelsViewSet(viewsets.ModelViewSet):
    """
    En este EndPoint se listan, activan y desactivan datos pertenecientes a
    una compañía.

    El JSON se debe escribir de la siguiente manera:

    {
    "action": "Enbles/Disabled"  # Acción a realizar sobre el dato
    "cause": "Test_cause",  # Causa por la que se desactivará el dato
    "company": "Test_company",  # Compañía a la que pertenece el dato
    "date": "yyyy-mm-dd",  # Fecha de la deshabilitación, default fecha actual
    "fk_object": Pk_model,  # Clave primaria del registro
    "model": "Test_model",  # Nombre del modelo al que pertenece el dato
    }

    lista de modelos:
    "brand",
    "item",
    "lostitem",
    "item",
    "visitor",
    "typeitem"
    Por razones técnicas no se desarrolló el sistema para desactivar user.
    """
    queryset = Disabled.objects.all()
    permission_classes = (DRYPermissions,)
    serializer_class = DisabledModelSerializer
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['fk_object']

    def list(self, request, company_pk):
        queryset_list = Disabled.objects.filter(
            company__id=company_pk
        )
        # query = self.request.GET.get("search")
        # if query:
        #     queryset_list = queryset_list.filter(
        #                 Q(fk_object=query)
        #                 ).distinct()
        #     serializer = DisabledSerializer(queryset_list, many=True)
        #     return Response(serializer.data)
        serializer = DisabledModelSerializer(queryset_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, company_pk):
        r_queryset = get_object_or_404(
                    Disabled,
                    id=pk,
                    company__id=company_pk
                    )
        serializer = DisabledModelSerializer(r_queryset)
        return Response(serializer.data)

    def create(self, request, company_pk):
        data = request.data.copy()
        model = request.data["model"]
        serializer = DisabledModelSerializer(data=data)
        user_company = str(request.user.customuser.seathasuser.seat.company_id)
        if serializer.is_valid():
            if data['company'] != user_company:
                return Response("El usuario no pertenece a esta compañía",
                                status=status.HTTP_403_FORBIDDEN)
            models = {'visitor': Visitor,
                      'typeitem': TypeItem, 'brand': Brand, 'item': Item,
                      'lostitem': LostItem}
            model_name = models[model]
            register_to_disable = get_object_or_404(
                                  model_name,
                                  id=data["fk_object"],
                                  )
            if serializer.validated_data['action']:
                if not register_to_disable.enabled:
                    register_to_disable.enabled = True
                else:
                    return Response({model: "Ya estaba activado"},
                                    status=status.HTTP_412_PRECONDITION_FAILED)
            else:
                if register_to_disable.enabled:
                    register_to_disable.enabled = False
                else:
                    return Response({model: "Ya estaba desactivado"},
                                    status=status.HTTP_412_PRECONDITION_FAILED)
            serializer.save()
            register_to_disable.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
