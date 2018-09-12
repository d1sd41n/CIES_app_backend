from django.db.models import F, Q
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from core.models import Seat, Company, CustomUser
from codes.models import Code
from dry_rest_permissions.generics import DRYPermissions
from items.models import Brand, CheckIn, Item, LostItem, TypeItem
from items.serializers import (BrandSerializer, CheckInCreateSerializer,
                               ChekinSerializer, ItemSerializer,
                               ItemUpdateSerializer, LostItemSerializer,
                               RegisterItem, TypeItemSerializer)


class CheckInViewSet(viewsets.ModelViewSet):
    """En este EndPoint se registra la entrada y salida del objeto a la sede

        El siguiente es el formato de JSON a usar:
        <pre>
        {
        "go_in": true/false,  # true si ingresa, false si sale
        "item": pk_item,  # Id del objeto que ingresa
        "seat": pk_seat,  # Id de la sede donde se realiza el último ingreso
        "worker": pk_worker  # Id del empleado que realiza el ingreso/salida
        }
        </pre>"""
    permission_classes = (DRYPermissions,)
    queryset = CheckIn.objects.all()
    serializer_class = CheckInCreateSerializer
    filter_backends = [SearchFilter]
    search_fields = ['item', 'worker']

    def create(self, request, company_pk, seat_pk):
        data = request.data
        try:
            Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"company":"Esa compañia no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            seat = Seat.objects.get(id=seat_pk, company__id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"seat":"esa sede no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=data['worker'])
        except ObjectDoesNotExist:
            return Response({"Error": {"worker":"ese usuario no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            CustomUser.objects.get(id=data['worker'], seat=seat_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"worker":"ese usuario es incorrecto"}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CheckInCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"Error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def queryAnnotate(self, checks):
        checks = checks \
            .values('id', 'date', 'go_in') \
            .annotate(seat_id=F('seat__id'), item_id=F('item'),
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

    def update(self, request, company_pk, seat_pk, pk, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RegisterItemViewSet(generics.CreateAPIView):
    """En este endpoint se registran los item.

    Se insertan datos específicos del objeto, exceptuando
    el tipo de objeto y su marca.

    Para registrar se debe enviar un JSON con el siguiente formato:

    {
    <pre>
    "reference": "test_reference",  # Referencia del objeto como una string
    "color": "test_color",  # Color del objeto como una string
    "description": "test_description",  # Descripción del objeto, una string
    "type_item": pk_type_item,  # Id del tipo de objeto
    "code": "test_hash", # Hash relacionado al código QR
    "owner": pk_owner,  # Id del dueño del objeto
    "brand": pk_brand  # Id de la marca del objeto
    </pre>
    }
    """

    permission_classes = (DRYPermissions,)
    serializer_class = RegisterItem

    def post(self, request, company_pk, seat_pk):
        data = request.data.copy()
        try:
            seat = Seat.objects.get(id=seat_pk, company__id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"seat":"esa sede no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            typeitem = TypeItem.objects.get(id=data['type_item'], company__pk=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"TypeItem":"No existe ese tipo de objeto"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            brand = Brand.objects.get(id=data['brand'], type_item__company=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"brand":"No existe ese tipo de objeto de esta marca"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            code = Code.objects.get(code=data['code'], seat=seat_pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"code":"Codigo invalido"}}, status=status.HTTP_400_BAD_REQUEST)
        if code.used:
            return Response({"Error":{"code":"ese codigo ya esta en uso"}}, status=status.HTTP_400_BAD_REQUEST)

        data['seat_registration'] = seat_pk
        data['lost'] = False
        data['enabled'] = True
        data['registration_date'] = timezone.now()
        serializer = RegisterItem(data=data)
        if serializer.is_valid():
            serializer.save(registered_by=request.user, enabled=True)
            code.used = True
            code.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"Error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemViewSet(viewsets.ModelViewSet):
    """"
    En este EndPoint se pueden ver todos los items registrados
    en una compañía con todos sus detalles, como dueño,
    DNI del dueño, la sede en que se registró,
    el empleado que lo registró, etc.

    Para modificar o ver información de un item específico se debe
    pasar la id del item como parametro a la URL, de la siguiente
    forma:

    http://localhost:8000/items/companies/pk/items/pk

    Este EndPoint solo lista y modifica,
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
    serializer_class = ItemUpdateSerializer
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
        if not len(items):
            return Response({"Error":{"item":"Este item no existe"}}, status=status.HTTP_404_NOT_FOUND)
        item = self.queryAnnotate(items)
        serializer = ItemSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, company_pk, pk, **kwargs):
        try:
            Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"company":"la compañia no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            typeitem = TypeItem.objects.get(id=request.data['type_item'], company__pk=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"TypeItem":"No existe ese tipo de objeto"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            brand = Brand.objects.get(id=request.data['brand'], type_item__company=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"brand":"No existe ese tipo de objeto de esta marca"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            item = Item.objects.get(id=pk, type_item__company=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"item":"No existe ese item"}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ItemUpdateSerializer(item, data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['lost']:
                serializer.validated_data['lost_date'] = timezone.now()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"Error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CompanyTypeItem(viewsets.ModelViewSet):
    """
    En este EndPoint se crean los tipos de objetos que ingresan a la compañía

    El siguiente es el formato JSON a usar:

    <pre>
    {
    "kind": "test_kind"  # Nombre del tipo de objeto a crear
    }
    </pre>

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
        try:
            Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"company":"la compañia no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        data["company"] = company_pk
        serializer = TypeItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"Error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, company_pk, **kwargs):
        data = request.data.copy()
        data['company'] = company_pk
        try:
            Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"company":"Esa compañia no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            typeitem = TypeItem.objects.get(id=pk, company__pk=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"TypeItem":"No existe ese tipo de objeto"}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TypeItemSerializer(typeitem, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(request.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"Error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class BrandItem(viewsets.ModelViewSet):
    """
    En este EndPoint se crean las marcas de los objetos de cada compañía

    El siguiente es el formato JSON a usar:
    <pre>
    {
    "brand": "test_brand"  # Marca del objeto como una string
    }
    </pre>

    se filtra con brand

    """
    permission_classes = (DRYPermissions,)
    queryset = Brand.objects.all().order_by(Lower('brand'))
    serializer_class = BrandSerializer
    filter_backends = [SearchFilter]
    search_fields = ['brand']

    def queryAnnotate(self, brands):
        brands = brands.values('id', 'brand', 'enabled'). \
            annotate(type_item=F('type_item__kind'))
        return brands

    def list(self, request, company_pk, typeitem_pk):
        queryset_list = Brand.objects.filter(
            type_item__company=company_pk,
            type_item=typeitem_pk,
            enabled=True
        ).order_by(Lower('brand'))
        brands = self.queryAnnotate(queryset_list)
        return Response(brands)

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
        try:
            Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"company":"Esa compañia no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            typeitem = TypeItem.objects.get(id=typeitem_pk, company__pk=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"TypeItem":"No existe ese tipo de objeto"}}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data["type_item"] = typeitem_pk

        serializer = BrandSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, company_pk, typeitem_pk, **kwargs):
        data = request.data.copy()
        data['company'] = company_pk
        try:
            Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"company":"Esa compañia no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            brand = Brand.objects.get(type_item=typeitem_pk, type_item__company=company_pk, id=pk)
        except ObjectDoesNotExist:
            return Response({"Error":{"item":"No existe ese tipo de objeto de esta marca"}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BrandSerializer(brand, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(request.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"Error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LostItemView(APIView):
    """
    En este endpoint se listan todos los objetos perdidos,

    **filtros pendientes**"""
    permission_classes = (DRYPermissions,)
    queryset = Item.objects.all()
    serializer_class = LostItemSerializer
    filter_backends = [SearchFilter]
    search_fields = ['owner_dni']

    def queryAnnotate(self, items):
        lostitems = items \
            .values('id', 'lost_date', 'color', 'reference', 'description', 'lost') \
            .annotate(type_item=F('type_item__kind'),
                      owner_dni=F('owner__dni'),
                      owner_email=F('owner__email'),
                      owner_phone=F('owner__phone'),
                      item_brand=F('brand__brand'),
                      owner_name=F('owner__first_name'),
                      owner_last_name=F('owner__last_name'),
                      lost_in_seat_id=F('seat_registration__id'),
                      lost_in_seat=F('seat_registration__name'))
        return lostitems

    def get(self, request, company_pk):
        lost_items = Item.objects.filter(seat_registration__company__id=company_pk,
                                         enabled=True, lost=True)
        query = self.request.GET.get("search")
        if query:
            lost_items = lost_items.filter(
                Q(owner__dni__iexact=query) |
                Q(brand__brand=query) |
                Q(type_item__kind=query)
            ).distinct()
        lost_items = self.queryAnnotate(lost_items)
        serializer = LostItemSerializer(lost_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
