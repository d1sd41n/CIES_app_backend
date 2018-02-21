from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models.functions import Lower
from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from ubication.models import Location
from core.models import Seat
from django.db.models import F, ExpressionWrapper


from items.models import (
    TypeItem,
    Brand,
    Item,
    LostItem,
    Checkin,
)

from items.serializers import (
    ItemSerializer,
    ChekinSerializer,
    TypeItemSerializer,
    Branderializer,
    RegisterItem,
)
class CheckInViewSet(viewsets.ModelViewSet):
    """"en este endpoint se registra la entrada de salida de ItemSerializer
        en la sede

    #####################################################
    este endpoint esta en construccion

    Faltan permisos, filtros y otros detalles de seguridad
    #####################################################"""
    queryset = Checkin.objects.all()
    serializer_class = ChekinSerializer


class RegisterItemViewSet(generics.CreateAPIView):
    """"en este endpoint se hacen los registros del item,
    solo eso, las consultas se hacen en otro endpoint"""

    serializer_class = RegisterItem


    def post(self, request, company_pk, seat_pk):
        print(request.data)
        data = request.data
        r_queryset = get_object_or_404(
                    Seat,
                    id=seat_pk,
                    company=company_pk,
                    enabled=True
                    )
        serializer = RegisterItem(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """"
    Aqui no se crean Items, eso será en otro endpoint,

    Este endpoint solo es de lectura, se consultan todos los datos
    de un item y su registro.

    #####################################################
    este endpoint esta en construccion

    Faltan permisos, filtros y test
    #####################################################"""
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def queryAnnotate(self, items):
        items = items \
                    .values('id', 'reference', 'description', 'lost', 'color', 'registration_date', 'registeredBy') \
                    .annotate(type_item=F('type_item__kind'), owner_name=F('owner__first_name'), \
                              owner_last_name=F('owner__last_name'), owner_dni=F('owner__dni'), \
                              brand=F('brand__brand'), registered_in_seat=F('seatRegistration__name'), \
                              registered_in_seat_id=F('seatRegistration'), company_id=F('seatRegistration__company'), \
                              code=F('code__code'))
        return items

    def list(self, request, company_pk):
        items = Item.objects.filter(type_item__company__id=company_pk, enabled=True)
        items = self.queryAnnotate(items)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, company_pk, pk):
        items = Item.objects.filter(pk=pk, type_item__company__id=company_pk, enabled=True)
        if (not len(items)):
            return Response(status=status.HTTP_404_NOT_FOUND)
        item = items = self.queryAnnotate(items)
        serializer = ItemSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanyTypeItem(viewsets.ModelViewSet):
    """


    {
    "kind": "carro"
    }

    """

    queryset = TypeItem.objects.all().order_by(Lower('kind'))
    serializer_class = TypeItemSerializer
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['name']

    def list(self, request, company_pk):
        queryset_list = TypeItem.objects.filter(
            company=company_pk,
            enabled=True
            ).order_by(
                Lower('kind')
            )
        # query = self.request.GET.get("last_name")
        # if query:
        #     queryset_list = queryset_list.filter(
        #                 Q(name__icontains=query)
        #                 ).distinct()
            # serializer = VisitorSerializer(queryset_list, many=True)
            # return Response(serializer.data)
        serializer = TypeItemSerializer(queryset_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, company_pk):
        r_queryset = get_object_or_404(
                    TypeItem,
                    id=pk,
                    company=company_pk,
                    enabled=True
                    )
        serializer = TypeItemSerializer(r_queryset)
        return Response(serializer.data)

    def create(self, request, company_pk):
        print(request.data)
        data = request.data.copy()
        data["company"] = company_pk
        serializer = TypeItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BrandItem(viewsets.ModelViewSet):
    """
    {
    "kind": "carro"
    }

    """

    queryset = Brand.objects.all().order_by(Lower('brand'))
    serializer_class = Branderializer
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['name']

    def list(self, request, company_pk, typeitem_pk):
        queryset_list = Brand.objects.filter(
            type_item__company=company_pk,
            type_item=typeitem_pk,
            enabled=True
            ).order_by(
                Lower('brand')
            )
        # query = self.request.GET.get("last_name")
        # if query:
        #     queryset_list = queryset_list.filter(
        #                 Q(name__icontains=query)
        #                 ).distinct()
            # serializer = VisitorSerializer(queryset_list, many=True)
            # return Response(serializer.data)
        serializer = Branderializer(queryset_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, company_pk, typeitem_pk):
        r_queryset = get_object_or_404(
                    Brand,
                    id=pk,
                    type_item__company=company_pk,
                    type_item=typeitem_pk,
                    enabled=True
                    )
        serializer = Branderializer(r_queryset)
        return Response(serializer.data)

    def create(self, request, company_pk, typeitem_pk):
        validator = get_object_or_404(
                    TypeItem,
                    company=company_pk,
                    pk=typeitem_pk,
                    enabled=True
                    )
        data = request.data.copy()
        data["company"] = company_pk
        data["type_item"] = typeitem_pk
        serializer = Branderializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
