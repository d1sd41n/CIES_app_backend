from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from core.models import (
    Company,
    Seat,
    CustomUser,
    Visitor,
    SeatHasUser,
)

from items.models import (
    TypeItem,
    Brand,
    Item,
    LostItem,
    Checkin,
    LostItem,
)
from disabled.models import Disabled
from disabled.serializers import (
    DisabledSerializer,
)
from ubication.models import Country, Region, City


class DisableCompanyViewSet(viewsets.ModelViewSet):
    """
    En este endpoint se listan y se desactivan compañias.
    el JSON se debe escribir de la siguiente manera:
    <pre>
    {
    "cause": "la compañia se quebro y se retira",
    "fk_object": 2,
    "date": "2017-10-04"
    }
    </pre>
    cause: la razon por la cual se desactiva la compañia.
    fk_object: la id de la compañia que se va a desactivar,
    el campo model del modelo Disabled se genera automaticamente al ahcer post.

    Al hacer post tambien automaticamente el campo enabled de dicha compañia pasa
    a ser False.

    Si se intenta desactivar una compañia que ya esta desactivada el servidor responderá
    con un estatus de '404'

    Aqui no es necesario espesificar que el modelo es "company"
    """
    queryset = Disabled.objects.all()
    serializer_class = DisabledSerializer
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['fk_object']

    def list(self, request):
        queryset_list = Disabled.objects.filter(
            model__model="company"
        )
        query = self.request.GET.get("search")
        if query:
            queryset_list = queryset_list.filter(
                        Q(fk_object=query)
                        ).distinct()
            serializer = DisabledSerializer(queryset_list, many=True)
            return Response(serializer.data)
        serializer = DisabledSerializer(queryset_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        r_queryset = get_object_or_404(
                    Disabled,
                    id=pk,
                    model__model="company"
                    )
        serializer = DisabledSerializer(r_queryset)
        return Response(serializer.data)

    def create(self, request):
        data = request.data.copy()
        print(request.data)
        contentTypeId = ContentType.objects.get(model="company").id
        print(contentTypeId)
        data["model"] = str(contentTypeId)
        serializer = DisabledSerializer(data=data)
        if serializer.is_valid():
            company = get_object_or_404(
                        Company,
                        id=data["fk_object"]
                        )
            if (not company.enabled):
                return Response({"company": "Ya estaba desactivada"}, status=status.HTTP_412_PRECONDITION_FAILED)
            company.enabled = False
            serializer.save()
            company.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DisableModelsViewSet(viewsets.ModelViewSet):
    """
    En este endpoint se listan y se desactivan modelos pertenecientes a una compañia.
    el JSON se debe escribir de la siguiente manera:
    <pre>
    {
    "cause": "el empleado se se quebro y se retira",
    "fk_object": 2,
    "date": "2017-10-04",
    "model": "user",
    "company": "1"
    }
    </pre>
    En el campo model se debe introducir el modelo al cual pertenece el objeto que se va a desactivar
    <pre>
    lista de modelos:
    "user",
    "brand",
    "item",
    "lostitem",
    "item",
    "seat",
    "visitor",
    "typeitem"
    </pre>
    en fk_object su id


    Por razones tecnicas no se desarrollo el sistema para desactivar user.

    """
    queryset = Disabled.objects.all()
    serializer_class = DisabledSerializer
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
        serializer = DisabledSerializer(queryset_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, company_pk):
        r_queryset = get_object_or_404(
                    Disabled,
                    id=pk,
                    company__id=company_pk
                    )
        serializer = DisabledSerializer(r_queryset)
        return Response(serializer.data)
    
    def create(self, request, company_pk):
        data = request.data.copy()
        model=request.data["model"]
        contentTypeId = ContentType.objects.get(model=model).id
        data["model"] = str(contentTypeId)
        serializer = DisabledSerializer(data=data)
        if serializer.is_valid():
            #core------------------------
            #seat
            if(model=="seat"):
                seat = get_object_or_404(
                            Seat,
                            id=data["fk_object"],
                            company__id=company_pk,
                            )
                if (not seat.enabled):
                    return Response({"seat": "Ya estaba desactivada"}, status=status.HTTP_412_PRECONDITION_FAILED)
                seat.enabled = False
                seat.save()
            #visitor
            elif(model=="visitor"):
                visitor = get_object_or_404(
                            Visitor,
                            id=data["fk_object"],
                            company__id=company_pk,
                            )
                if (not visitor.enabled):
                    return Response({"visitor": "Ya estaba desactivada"}, status=status.HTTP_412_PRECONDITION_FAILED)
                visitor.enabled = False
                visitor.save()
            
             #user
            # elif(model=="customuser"):
            #     print(33333333333333, contentTypeId)
            #     customuser = get_object_or_404(
            #                 CustomUser,
            #                 id=data["fk_object"],
            #                 company__id=company_pk,
            #                 )
            #     if (not customuser.enabled):
            #         return Response({"customuser": "Ya estaba desactivada"}, status=status.HTTP_412_PRECONDITION_FAILED)
            #     customuser.enabled = False
            #     customuser.save()

            #items-----------------------------
            #TypeItem
            elif(model=="typeitem"):
                typeitem = get_object_or_404(
                            TypeItem,
                            id=data["fk_object"],
                            company__id=company_pk,
                            )
                if (not typeitem.enabled):
                    return Response({"typeitem": "Ya estaba desactivada"}, status=status.HTTP_412_PRECONDITION_FAILED)
                typeitem.enabled = False
                typeitem.save()
            
            #Brand
            elif(model=="brand"):
                brand = get_object_or_404(
                            Brand,
                            id=data["fk_object"],
                            type_item__company__id=company_pk,
                            )
                if (not brand.enabled):
                    return Response({"brand": "Ya estaba desactivada"}, status=status.HTTP_412_PRECONDITION_FAILED)
                brand.enabled = False
                brand.save()
            
            #item
            elif(model=="item"):
                item = get_object_or_404(
                            Item,
                            id=data["fk_object"],
                            brand__type_item__company__id=company_pk,
                            )
                if (not item.enabled):
                    return Response({"item": "Ya estaba desactivada"}, status=status.HTTP_412_PRECONDITION_FAILED)
                item.enabled = False
                item.save()
            
            #lostitem
            elif(model=="lostitem"):
                print(3333, contentTypeId)
                lostitem = get_object_or_404(
                            LostItem,
                            id=data["fk_object"],
                            item__brand__type_item__company__id=company_pk,
                            )
                if (not lostitem.enabled):
                    return Response({"item": "Ya estaba desactivada"}, status=status.HTTP_412_PRECONDITION_FAILED)
                lostitem.enabled = False
                lostitem.save()


            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
