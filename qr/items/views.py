from django.db.models import F, Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from core.models import Seat
from dry_rest_permissions.generics import DRYPermissions
from items.models import Brand, CheckIn, Item, LostItem, TypeItem
from items.serializers import (BrandSerializer, CheckInCreateSerializer,
                               ChekinSerializer, ItemSerializer,
                               LostItemCreateSerializer, LostItemSerializer,
                               RegisterItem, TypeItemSerializer)


class CheckInViewSet(viewsets.ModelViewSet):
    """En este EndPoint se registra la entrada y salida del objeto a la sede

        El siguiente es el formato de JSON a usar:

        {
        "go_in": true/false,  # true si ingresa, false si sale
        "item": pk_item,  # Id del objeto que ingresa
        "seat": pk_seat,  # Id de la sede donde se realiza el último ingreso
        "worker": pk_worker  # Id del empleado que realiza el ingreso/salida
        }"""
    permission_classes = (DRYPermissions,)
    queryset = CheckIn.objects.all()
    serializer_class = CheckInCreateSerializer
    filter_backends = [SearchFilter]
    search_fields = ['item', 'worker']

    def create(self, request, company_pk, seat_pk):
        data = request.data
        serializer = CheckInCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def queryAnnotate(self, checks):
        checks = checks \
            .values('id', 'item', 'date', 'go_in') \
            .annotate(seat_id=F('seat__id'),
                      seat_dir=F('seat__address__address'),
                      owner_last_name=F('item__owner__last_name'),
                      owner_dni=F('item__owner__dni'),
                      type_item=F('item__type_item__kind'),
                      owner_name=F('item__owner__first_name'),
                      lost=F('item__lost'),)
        return checks

    def list(self, request, company_pk, seat_pk):
        checks = CheckIn.objects.filter(seat__company__id=company_pk,
                                        seat__id=seat_pk)
        query = self.request.GET.get("last_name")
        if query:
            queryset_list = queryset_list.filter(
                Q(item__owner__dni__icontains=query)
            ).distinct()
            serializer = VisitorSerializer(queryset_list, many=True)
            return Response(serializer.data)
        checks = self.queryAnnotate(checks)
        serializer = ChekinSerializer(checks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, company_pk, seat_pk, pk):
        checks = CheckIn.objects.filter(seat__company__id=company_pk,
                                        seat__id=seat_pk, id=pk)
        if (not len(checks)):
            return Response(status=status.HTTP_404_NOT_FOUND)
        checks = self.queryAnnotate(checks)
        serializer = ChekinSerializer(checks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterItemViewSet(generics.CreateAPIView):
    """En este endpoint se registran los item.

    Se insertan datos específicos del objeto, exceptuando
    el tipo de objeto y su marca.

    Para registrar se debe enviar un JSON con el siguiente formato:

    {
    "reference": "test_reference",  # Referencia del objeto como una string
    "color": "test_color",  # Color del objeto como una string
    "description": "test_description",  # Descripción del objeto, una string
    "lost": true/false, # true si el objeto está perdido, false si no
    "enabled": true/false, # true si el objeto está habilitado, false si no
    "registration_date": "yyyy-mm-dd",  # Fecha del registro, default actual
    "type_item": pk_type_item,  # Id del tipo de objeto
    "code": "test_hash", # Hash relacionado al código QR
    "owner": pk_owner,  # Id del dueño del objeto
    "brand": pk_brand,  # Id de la marca del objeto
    "seat_registration": pk_seat, # Id de la sede donde se registró el objeto
    "registered_by": pk_worker  # Id del empleado que registró el objeto
    }
    """

    permission_classes = (DRYPermissions,)
    serializer_class = RegisterItem

    def post(self, request, company_pk, seat_pk):
        data = request.data
        if str(data['seat_registration']) != str(seat_pk):
            return Response('El ingreso no se realizó en esta sede',
                            status=status.HTTP_400_BAD_REQUEST)
        r_queryset = get_object_or_404(
            Seat,
            id=seat_pk,
            company=company_pk,
            enabled=True
        )
        serializer = RegisterItem(data=data)
        if serializer.is_valid():
            serializer.save(registered_by=request.user, enabled=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """"
    En este EndPoint se pueden ver todos los items registrados
    en una compañía con todos sus detalles, como dueño,
    DNI del dueño, la sede en que se registró,
    el empleado que lo registró, etc.

    Este EndPoint es de sólo lectura,
    para registrar items ir a la siguiente ruta:

    (http://localhost:8000/items/companies/pk/seats/pk/registeritem/)

    Se puede buscar por medio del DNI del dueño:
    (http://localhost:8000/items/companies/pk/items/?search=owner__dni)

    se filtra usando los campos:
    type item
    brand
    owner name
    owner last_name
    owner dni"""

    permission_classes = (DRYPermissions,)
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [SearchFilter]
    search_fields = ['owner dni']

    def queryAnnotate(self, items):
        items = items \
            .values('id', 'reference', 'description', 'lost', 'color',
                    'registration_date', 'registered_by') \
            .annotate(type_item=F('type_item__kind'),
                      owner_name=F('owner__first_name'),
                      owner_last_name=F('owner__last_name'),
                      owner_dni=F('owner__dni'),
                      brand=F('brand__brand'),
                      registered_in_seat=F('seat_registration__name'),
                      registered_in_seat_id=F('seat_registration'),
                      company_id=F('seat_registration__company'),
                      code=F('code__code'))
        return items

    def list(self, request, company_pk):
        items = Item.objects.filter(type_item__company__id=company_pk,
                                    enabled=True)
        query = self.request.GET.get("search")
        if query:
            items = items.filter(
                Q(owner__dni__iexact=query) |
                Q(type_item__kind__iexact=query) |
                Q(owner__first_name__iexact=query) |
                Q(owner__last_name__iexact=query) |
                Q(brand__brand__iexact=query)
            ).distinct()
        items = self.queryAnnotate(items)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, company_pk, pk):
        items = Item.objects.filter(pk=pk, type_item__company__id=company_pk,
                                    enabled=True)
        if (not len(items)):
            return Response(status=status.HTTP_404_NOT_FOUND)
        item = self.queryAnnotate(items)
        serializer = ItemSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanyTypeItem(viewsets.ModelViewSet):
    """
    En este EndPoint se crean los tipos de objetos que ingresan a la compañía

    El siguiente es el formato JSON a usar:

    {
    "kind": "test_kind"  # Nombre del tipo de objeto a crear
    "enabled": true/false  # true si está habilitado, false si no
    "company": pk_company  # Id de la compañía
    }

    se filtra con: kind
    """
    permission_classes = (DRYPermissions,)
    queryset = TypeItem.objects.all().order_by(Lower('kind'))
    serializer_class = TypeItemSerializer
    filter_backends = [SearchFilter]
    search_fields = ['kind']

    def list(self, request, company_pk):
        queryset_list = TypeItem.objects.filter(
            company=company_pk,
            enabled=True
        ).order_by(
            Lower('kind')
        )
        query = self.request.GET.get("search")
        if query:
            queryset_list = queryset_list.filter(
                Q(kind__icontains=query)
            ).distinct()
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
        data = request.data.copy()
        data["company"] = company_pk
        serializer = TypeItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BrandItem(viewsets.ModelViewSet):
    """
    En este EndPoint se crean las marcas de los objetos de cada compañía

    El siguiente es el formato JSON a usar:

    {
    "brand": "test_brand"  # Marca del objeto como una string
    "enabled": true/false  # true si está habilitado, false si no
    "type_item": pk_type_item  # Id del tipo de item
    }

    se filtra con brand

    """
    permission_classes = (DRYPermissions,)
    queryset = Brand.objects.all().order_by(Lower('brand'))
    serializer_class = BrandSerializer
    filter_backends = [SearchFilter]
    search_fields = ['brand']

    def list(self, request, company_pk, typeitem_pk):
        queryset_list = Brand.objects.filter(
            type_item__company=company_pk,
            type_item=typeitem_pk,
            enabled=True
        ).order_by(
            Lower('brand')
        )
        query = self.request.GET.get("search")
        if query:
            queryset_list = queryset_list.filter(
                Q(brand__icontains=query)
            ).distinct()
        serializer = BrandSerializer(queryset_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, company_pk, typeitem_pk):
        r_queryset = get_object_or_404(
            Brand,
            id=pk,
            type_item__company=company_pk,
            type_item=typeitem_pk,
            enabled=True
        )
        serializer = BrandSerializer(r_queryset)
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
        serializer = BrandSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LostItemView(viewsets.ModelViewSet):
    """
    En este endpoint se reigstran los item perdidos,
    este es el JSON de ejemplo
    <pre>
    {
    "description": "test_description",  # Descripción del objeto perdido,
    como una string
    "date": "aa-mm-dd hh:mm:ss.ff",  # Fecha en que se perdió el objeto,
    default la actual
    "email": "test_email@testserver.test",  # Email del dueño del objeto,
    como una string
    "visitor_phone": "test_phone",  # Teléfono del dueño del objeto, un int
    "item": test_pk,  # Clave primaria del objeto
    "seat": test_pk  # Clave primaria de la sede donde sucedió la pérdida
    }
    </pre>
    """

    queryset = LostItem.objects.all()
    serializer_class = LostItemCreateSerializer
    filter_backends = [SearchFilter]
    search_fields = ['owner_dni']

    def queryAnnotate(self, items):
        lostitems = items \
            .values('id', 'date', 'description', 'email',
                    'visitor_phone', 'closed_case') \
            .annotate(item_reference=F('item__reference'),
                      item_color=F('item__color'),
                      type_item=F('item__type_item__kind'),
                      owner_dni=F('item__owner__dni'),
                      item_brand=F('item__brand__brand'),
                      owner_name=F('item__owner__first_name'),
                      owner_last_name=F('item__owner__last_name'),
                      lost_in_seat_id=F('seat__id'),
                      lost_in_seat=F('seat__name'))
        return lostitems

    def list(self, request, company_pk):
        lost_items = LostItem.objects.filter(seat__company__id=company_pk,
                                             enabled=True)
        query = self.request.GET.get("search")
        if query:
            lost_items = lost_items.filter(
                Q(item__owner__dni__iexact=query) |
                Q(item__brand__brand=query) |
                Q(item__type_item__kind=query)
            ).distinct()
        lost_items = self.queryAnnotate(lost_items)
        serializer = LostItemSerializer(lost_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, company_pk, pk):
        lost_items = LostItem.objects.filter(pk=pk,
                                             seat__company__id=company_pk,
                                             enabled=True)
        if (not len(lost_items)):
            return Response(status=status.HTTP_404_NOT_FOUND)
        lost_items = self.queryAnnotate(lost_items)
        serializer = LostItemSerializer(lost_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
