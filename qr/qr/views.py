from django.contrib.auth.models import Group, User

from core.models import Company, CustomUser, Seat, Visitor
from core.serializers import (AddressSerializer, CompanySerializer,
                              CustomUserSerializer, SeatSerializer,
                              SeatSerializerList, UserSerializer,
                              UserSerializerEdit, UserSerializerListCustom,
                              VisitorSerializer, VisitorExistSerializer)

from ubication.models import *

from items.models import Brand, CheckIn, Item, LostItem, TypeItem
from items.serializers import (BrandSerializer, CheckInCreateSerializer,
                               ChekinSerializer, ItemSerializer,
                               ItemUpdateSerializer, LostItemSerializer,
                               RegisterItem, TypeItemSerializer)

from codes.models import *

from rest_framework.response import Response
from rest_framework.views import APIView

from qr.permissions import DeveloperOnly


from rest_framework import generics, status, viewsets
from django.db.models import F, Q
from qr.permissions import DeveloperOnly





class DebugDB(APIView):

    permission_classes = [DeveloperOnly,]
    """
    Esto solamente se usara para debuguear la base de datos
    siempre que no se vaya a usar ningun metodo estara habilitado ni
    la URL que conduce a esta view.

    El codigo que haya en los metodos, cambiara constantemente segun lo que
    se este realizando...
    """

    def get(self, request, format=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        # queryset_list = Visitor.objects.filter(
        #     company__pk=1
        # )
        # serializer = VisitorSerializer(queryset_list, many=True)
        # return Response(serializer.data)

    def post(self, request, format=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
