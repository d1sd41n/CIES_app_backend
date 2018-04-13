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
from rest_framework.filters import (
    SearchFilter,
)


from items.models import (
    TypeItem,
    Brand,
    Item,
    LostItem,
    Checkin,
    LostItem,
)

from items.serializers import (
    ItemSerializer,
    ChekinSerializer,
    TypeItemSerializer,
    Branderializer,
    RegisterItem,
    ChekinCreateSerializer,
    LostItemCreateSerializer,
    LostItemSerializer,
)
class CheckInViewSet(viewsets.ModelViewSet):
    """"en este endpoint se registra la entrada de salida de ItemSerializer
        en la sede

        Ejemplo de JSON:

        {
        "go_in": false,
        "item": 1,
        "seat": 1,
        "worker": 3
        }

        se debe introducir el un booleano true si va de entrada y false si es de salida
        la id de la sede, id del item e id del trabajador que lo escanea.

    #####################################################
    este endpoint esta en construccion

    Faltan permisos, filtros y otros detalles de seguridad
    #####################################################"""
    queryset = Checkin.objects.all()
    serializer_class = ChekinCreateSerializer

    def create(self, request, company_pk, seat_pk):
        data = request.data
        # r_queryset = get_object_or_404(
        #             Seat,
        #             id=seat_pk,
        #             company=company_pk,
        #             enabled=True
        #             )
        serializer = ChekinCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def queryAnnotate(self, checks):
        checks = checks \
                    .values('id', 'item', 'date', 'go_in') \
                    .annotate(seat_id=F('seat__id'), seat_dir=F('seat__address__address'), \
                              owner_last_name=F('item__owner__last_name'), owner_dni=F('item__owner__dni'), \
                              type_item=F('item__type_item__kind'), owner_name=F('item__owner__first_name'), \
                              lost=F('item__lost'),)
        return checks

    def list(self, request, company_pk, seat_pk):
        print("dfwfefgefhehef")
        checks = Checkin.objects.filter(seat__company__id=company_pk, seat__id=seat_pk)
        # query = self.request.GET.get("last_name")
        # if query:
        #     queryset_list = queryset_list.filter(
        #                 Q(name__icontains=query)
        #                 ).distinct()
            # serializer = VisitorSerializer(queryset_list, many=True)
            # return Response(serializer.data)
        checks = self.queryAnnotate(checks)
        serializer = ChekinSerializer(checks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, company_pk, seat_pk, pk):
        checks = Checkin.objects.filter(seat__company__id=company_pk, seat__id=seat_pk, id=pk)
        if (not len(checks)):
            return Response(status=status.HTTP_404_NOT_FOUND)
        checks = self.queryAnnotate(checks)
        serializer = ChekinSerializer(checks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class RegisterItemViewSet(generics.CreateAPIView):
    """"en este endpoint se registran los item,

    Solo el item como tal, la marca y el tipo de item se hace en otros
    endpoint.   Tambien la consulta de todos los teims existentes.

    Para registrar se debe enviar un JSON con el siguiente formato:

    Ejemplo de JSON:

    <pre>
    {
    "reference": "sqd",
    "color": "rojo",
    "description": "grande sucio y feo",
    "lost": false,
    "enabled": false,
    "registration_date": "2018-03-20",
    "type_item": 1,
    "code": "44c5868b-b27a-4ca7-809c-ca1c1c42f1be",
    "owner": 1,
    "brand": 1,
    "seatRegistration": 1,
    "registeredBy": 3
    }
    </pre>

    los campos owner, brand, seatRegistration, registeredBy, type_item

    llevan las id del dueño del producto, la marca , la sede, el empleado que lo registrados
    y el tipo de item.

    """

    serializer_class = RegisterItem


    def post(self, request, company_pk, seat_pk):
        data = request.data
        if(str(data['seat_registration']) != str(seat_pk)):
            return Response(status=status.HTTP_400_BAD_REQUEST)
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
    En este endpoint se pueden ver todos los items registrados
    en una compañia, junto a todos sus detalles, como dueño,
    dni del dueño, la sede en que se registro, el empleado que lo registro,
    entre otros...

    Este enpoint solo es de lectura, por el cualaqui no se registran items,
    eso se ahce en la siguiente ruta:

    (http://localhost:8000/items/companies/id/seats/id/registeritem/)

    Se puede Buscar por medio de el dni de el dueño:
    (http://localhost:8000/items/companies/1/items/?search=[dni de el sueño])
    sin los []

    #####################################################
    este endpoint esta en construccion

    Faltan permisos
    #####################################################"""
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [SearchFilter]
    search_fields = ['owner dni']

    def queryAnnotate(self, items):
        items = items \
                    .values('id', 'reference', 'description', 'lost', 'color', 'registration_date', 'registered_by') \
                    .annotate(type_item=F('type_item__kind'), owner_name=F('owner__first_name'), \
                              owner_last_name=F('owner__last_name'), owner_dni=F('owner__dni'), \
                              brand=F('brand__brand'), registered_in_seat=F('seat_registration__name'), \
                              registered_in_seat_id=F('seat_registration'), company_id=F('seat_registration__company'), \
                              code=F('code__code'))
        return items

    def list(self, request, company_pk):
        items = Item.objects.filter(type_item__company__id=company_pk, enabled=True)
        query = self.request.GET.get("search")
        if query:
            items = items.filter(
                        Q(owner__dni__iexact=query)
                        ).distinct()
        items = self.queryAnnotate(items)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, company_pk, pk):
        items = Item.objects.filter(pk=pk, type_item__company__id=company_pk, enabled=True)
        if (not len(items)):
            return Response(status=status.HTTP_404_NOT_FOUND)
        item = self.queryAnnotate(items)
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
        # query = self.request.GET.get("search")
        # if query:
        #     queryset_list = queryset_list.filter(
        #                 Q(name__icontains=query)
        #                 ).distinct()
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
        data["type_item"] = typeitem_pk
        serializer = Branderializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LostItemView(viewsets.ModelViewSet):
    """
    endpoint de items perdidos,
    este es el JSON con el que se registran items perdidos
    <pre>
    {
    "description": "el tonto del culo dejo el portatil en una mesa sola y alguien se lo agarro sin que se diera nicuenta",
    "date": "2018-03-01T18:11:12.425748-05:20",
    "email": "tocameernesto@gmail.com",
    "visitor_phone": "123456",
    "item": 2,
    "seat": 1
    }
    </pre>

    en el campo item y seats van las id de los correspondientes.

    Faltan filtros y permisos
    """


    queryset = LostItem.objects.all()
    serializer_class = LostItemCreateSerializer
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['name']

    # def create(self, request, company_pk):
    #     print(request.data)

    def queryAnnotate(self, items):
        lostitems = items \
                    .values('id', 'date', 'description', 'email', 'visitor_phone', 'closed_case') \
                    .annotate(item_reference=F('item__reference'), item_color=F('item__color'), \
                              type_item=F('item__type_item__kind'), owner_dni=F('item__owner__dni'), \
                              item_brand=F('item__brand__brand'), owner_name=F('item__owner__first_name'), \
                              owner_last_name=F('item__owner__last_name'), lost_in_seat_id=F('seat__id'), \
                              lost_in_seat=F('seat__name'))
        return lostitems

    def list(self, request, company_pk):
        lost_items = LostItem.objects.filter(seat__company__id=company_pk, enabled=True)
        query = self.request.GET.get("search")
        # if query:
        #     items = items.filter(
        #                 Q(owner__dni__iexact=query)
        #                 ).distinct()
        lost_items = self.queryAnnotate(lost_items)
        serializer = LostItemSerializer(lost_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, company_pk, pk):
        lost_items = LostItem.objects.filter(pk=pk, seat__company__id=company_pk, enabled=True)
        if (not len(lost_items)):
            return Response(status=status.HTTP_404_NOT_FOUND)
        lost_items = self.queryAnnotate(lost_items)
        serializer = LostItemSerializer(lost_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
