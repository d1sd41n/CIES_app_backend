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
)
class CheckInViewSet(viewsets.ModelViewSet):
    """"en este endpoint se hacen los registros del item,
    solo eso, las consultas se hacen en otro endpoint

    #####################################################
    este endpoint esta en construccion
    #####################################################"""
    queryset = Checkin.objects.all()
    serializer_class = ChekinSerializer


class RegisterItemViewSet(viewsets.ModelViewSet):
    """"en este endpoint se hacen los registros del item,
    solo eso, las consultas se hacen en otro endpoint

    #####################################################
    este endpoint esta en construccion Genera ERROR
    #####################################################"""
    queryset = Item.objects.all()
    serializer_class = ItemSerializer



class ItemViewSet(viewsets.ModelViewSet):
    """"
    Aqui no se crean Items, eso será en otro endpoint

    #####################################################
    este endpoint esta en construccion
    #####################################################"""
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def list(self, request, company_pk):
        items = Item.objects \
                    .values('id', 'reference', 'description', 'lost', 'color') \
                    .annotate(type_item=F('type_item__kind'), owner_name=F('owner__first_name'), \
                              owner_last_name=F('owner__last_name'), owner_dni=F('owner__dni'), \
                              brand=F('brand__brand'), registered_in=F('seatRegistration__name'))

        print(items)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
