from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from codes.models import Code
from core.models import Company, CustomUser, Seat, Visitor
from items.models import Brand, CheckIn, Item, LostItem, TypeItem
from items.serializers import (BrandSerializer, CheckInCreateSerializer,
                               ChekinSerializer, ItemSerializer,
                               ItemUpdateSerializer, LostItemSerializer,
                               RegisterItem, TypeItemSerializer)
from qr.permissions import (DeveloperOnly, ManagerAndSuperiorsOnly,
                            SupervisorAndSuperiorsOnly, GuardAndSuperiorsOnly)


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
        </pre>

        en este endpoint se puede filtrar por el id del Item
        para hacerlo:

        http://localhost:8000/items/companies/pk/seats/1pk/check/?search_item=ID_DEL_ITEM"""
    queryset = CheckIn.objects.all()
    permission_classes = [GuardAndSuperiorsOnly]
    serializer_class = CheckInCreateSerializer
    filter_backends = [SearchFilter]
    search_fields = ['item', 'worker']

    def create(self, request, company_pk, seat_pk):
        data = request.data.copy()
        try:
            company = Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"company": ["la compañia a la que intenta acceder no existe"]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            seat = Seat.objects.get(id=seat_pk, company__id=company_pk)
        except ObjectDoesNotExist:
            return Response({"seat": ["La sede a la que intenta acceder no existe"]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CheckInCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.validated_data['seat'] = seat
            serializer.validated_data['worker'] = request.user
            check = serializer.save()
            check.item.company.add(company)
            check.item.owner.company.add(company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def queryAnnotate(self, checks):
        checks = checks \
            .values('id', 'date', 'go_in') \
            .annotate(seat_id=F('seat__id'), item_id=F('item'),
                      seat_dir=F('seat__address__address'),
                      seat_name=F('seat__name'),
                      owner_dni=F('item__owner__dni'),
                      owner_name=F('item__owner__first_name'),
                      owner_last_name=F('item__owner__last_name'),
                      type_item=F('item__type_item__kind'),
                      brand=F('item__brand__brand'),
                      reference=F('item__reference'),
                      lost=F('item__lost'))
        return checks

    def list(self, request, company_pk, seat_pk):
        checks = CheckIn.objects.filter(seat__company__id=company_pk,
                                        seat__id=seat_pk).order_by('-date')
        query = self.request.GET.get("search_item")
        if query:
            checks = checks.filter(
                Q(item__id__iexact=query)
            ).distinct()
            if (not len(checks)):
                return Response({"Error": {"item": "Item no encontrado"}}, status=status.HTTP_404_NOT_FOUND)
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

    def destroy(self, request, company_pk, seat_pk, pk):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RegisterItemViewSet(generics.CreateAPIView):
    """En este endpoint se registran los item.

    Se insertan datos específicos del objeto, exceptuando
    el tipo de objeto y su marca.
    http://localhost:8000/items/companies/pk/seats/pk/registeritem/
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
    serializer_class = RegisterItem
    permission_classes = [GuardAndSuperiorsOnly]

    def post(self, request, company_pk, seat_pk):
        data = request.data.copy()

        try:
            seat = Seat.objects.get(id=seat_pk, company__id=company_pk)
        except ObjectDoesNotExist:
            return Response({"seat": ["la compañia a la que intenta acceder no existe"]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            typeitem = TypeItem.objects.get(
                id=data['type_item'])
        except ObjectDoesNotExist:
            return Response({"type_item": ["No existe ese tipo de objeto"]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            brand = Brand.objects.get(
                id=data['brand'])
        except ObjectDoesNotExist:
            return Response({"brand": ["No existe ese tipo de objeto de esta marca"]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            code = Code.objects.get(code=data['code'])
        except ObjectDoesNotExist:
            return Response({"code": ["Codigo invalido"]}, status=status.HTTP_400_BAD_REQUEST)
        if code.used:
            return Response({"code": ["ese codigo ya esta siendo usado"]}, status=status.HTTP_400_BAD_REQUEST)


        data['lost'] = False
        data['registration_date'] = timezone.now()
        serializer = RegisterItem(data=data)
        if serializer.is_valid():
            serializer.validated_data['seat_registration'] = seat
            item = serializer.save(registered_by=request.user, enabled=True)
            code.used = True
            code.save()
            company = Company.objects.get(pk=company_pk)
            visitor = Visitor.objects.get(pk=data['owner'])
            visitor.company.add(company)
            item.company.add(company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    con el codigo de codes

    usando search_code como variable de busqueda.

    ejemplo:
    http://localhost:8000/items/companies/1/items/?search_code=ad6e1ec9-fa89-486d-9328-6e9362d34162"""

    queryset = Item.objects.all()
    serializer_class = ItemUpdateSerializer
    filter_backends = [SearchFilter]
    search_fields = ['owner dni']
    permission_classes = [GuardAndSuperiorsOnly]

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
                      code=F('code__code'))
        return items

    def list(self, request, company_pk):
        items = Item.objects.filter(
            company__pk=company_pk,
            owner__company__pk=company_pk,
        )
        query = self.request.GET.get("search")
        if query:
            items = items.filter(
                Q(owner__dni__iexact=query) |
                Q(type_item__kind__iexact=query) |
                Q(owner__first_name__iexact=query) |
                Q(owner__last_name__iexact=query) |
                Q(brand__brand__iexact=query)
            ).distinct()
            if (not len(items)):
                return Response({"item": "Item no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        query = self.request.GET.get("search_code") # this filters by codes
        if query:
            items = items.filter(
                Q(code__pk=query)
            ).distinct()
            try:
                if (not len(items)):
                    return Response({"item": "Item no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            except ValidationError:
                return Response({"search_code": "Codigo invalido"}, status=status.HTTP_404_NOT_FOUND)
        items = self.queryAnnotate(items)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, company_pk, pk):
        items = Item.objects.filter(pk=pk, company__pk=company_pk, owner__company__pk=company_pk,)
        if not len(items):
            return Response({"item": "Este item no existe o no ha pasado por esta compañia"}, status=status.HTTP_404_NOT_FOUND)
        item = self.queryAnnotate(items)
        serializer = ItemSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, company_pk, pk, **kwargs):

        # esta es una solucion temporal al cambio de estado de obejto perdido
        #############################################################
        if len(request.data)==1 and 'lost' in request.data:
            try:
                item = Item.objects.get(id=pk, company__pk=company_pk, owner__company__pk=company_pk,)
            except ObjectDoesNotExist:
                return Response({"item": ["Este item no existe o no ha pasado por esta compañia"]}, status=status.HTTP_400_BAD_REQUEST)
            item.lost = request.data['lost']
            item.save()
            return Response({"lost": "cambiado estado de item"},
                            status=status.HTTP_201_CREATED)
        ################################################################

        request.data.pop("id", None)
        request.data.pop("registration_date", None)
        request.data.pop("seat_registration", None)
        request.data.pop("registered_by", None)

        if 'type_item' in request.data:
            try:
                typeitem = TypeItem.objects.get(
                    id=request.data['type_item'])
            except ObjectDoesNotExist:
                return Response({"type_item": ["No existe ese tipo de objeto"]}, status=status.HTTP_400_BAD_REQUEST)
        elif 'brand' in request.data:
            try:
                brand = Brand.objects.get(
                    id=request.data['brand'])
            except ObjectDoesNotExist:
                return Response({"brand": ["No existe ese tipo de objeto para esa marca"]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            item = Item.objects.get(id=pk, company__pk=company_pk, owner__company__pk=company_pk,)
        except ObjectDoesNotExist:
            return Response({"item": ["Este item no existe o no ha pasado por esta compañia"]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ItemUpdateSerializer(item, data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['lost']:
                serializer.validated_data['lost_date'] = timezone.now()
            try:
                code = Code.objects.get(code=request.data['code'])
            except ObjectDoesNotExist:
                return Response({"code": ["Codigo invalido"]}, status=status.HTTP_400_BAD_REQUEST)
            if code.used:
                if item.code != code:
                    return Response({"code": ["ese codigo ya esta en uso"]}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            code.used = True
            code.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk, company_pk, **kwargs):

        request.data.pop("id", None)
        request.data.pop("registration_date", None)
        request.data.pop("seat_registration", None)
        request.data.pop("registered_by", None)

        if 'type_item' in request.data:
            try:
                typeitem = TypeItem.objects.get(
                    id=request.data['type_item'])
            except ObjectDoesNotExist:
                return Response({"type_item": ["No existe ese tipo de objeto"]}, status=status.HTTP_400_BAD_REQUEST)
        elif 'brand' in request.data:
            try:
                brand = Brand.objects.get(
                    id=request.data['brand'])
            except ObjectDoesNotExist:
                return Response({"brand": ["No existe ese tipo de objeto para esa marca"]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            item = Item.objects.get(id=pk, company__pk=company_pk, owner__company__pk=company_pk,)
        except ObjectDoesNotExist:
            return Response({"item": ["Este item no existe o no ha pasado por esta compañia"]}, status=status.HTTP_400_BAD_REQUEST)


        serializer = ItemUpdateSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            if 'lost' in request.data:
                if serializer.validated_data['lost']:
                    serializer.validated_data['lost_date'] = timezone.now()
            if 'code' in request.data:
                try:
                    code = Code.objects.get(code=request.data['code'])
                except ObjectDoesNotExist:
                    return Response({"code": ["Codigo invalido"]}, status=status.HTTP_400_BAD_REQUEST)
                if code.used:
                    if item.code != code:
                        return Response({"code": ["ese codigo ya esta en uso"]}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            if 'code' in request.data:
                code.used = True
                code.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"Error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, company_pk, pk,):
        try:
            item = Item.objects.get(id=pk, company__pk=company_pk, owner__company__pk=company_pk,)
        except ObjectDoesNotExist:
            return Response({"item": ["Este item no existe o no ha pasado por esta compañia"]}, status=status.HTTP_400_BAD_REQUEST)
        item.delete()
        return Response({"item": "Item eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)


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
    queryset = TypeItem.objects.all().order_by(Lower('kind'))
    permission_classes = [GuardAndSuperiorsOnly]
    serializer_class = TypeItemSerializer
    filter_backends = [SearchFilter]
    search_fields = ['kind']

    def list(self, request, company_pk):
        queryset_list = TypeItem.objects.filter(
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
            enabled=True
        )
        serializer = TypeItemSerializer(r_queryset)
        return Response(serializer.data)

    def create(self, request, company_pk):
        """Este metodo se encuentra des-habilitado"""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        data = request.data
        serializer = TypeItemSerializer(data=data)
        try:
            company = Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"company": ["La compañía no está registrada"]}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.validated_data['company'] = company
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"Error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, company_pk, **kwargs):
        """Este metodo se encuentra des-habilitado"""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        data = request.data.copy()
        try:
            company = Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"company": ["la compañia no existe"]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            typeitem = TypeItem.objects.get(id=pk, company__pk=company_pk)
        except ObjectDoesNotExist:
            return Response({"TypeItem": "No existe ese tipo de objeto"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TypeItemSerializer(typeitem, data=data)
        if serializer.is_valid():
            serializer.validated_data['company'] = company
            serializer.save()
            return Response(request.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        def destroy(self, request, pk, company_pk):
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
    queryset = Brand.objects.all().order_by(Lower('brand'))
    serializer_class = BrandSerializer
    filter_backends = [SearchFilter]
    permission_classes = [GuardAndSuperiorsOnly]
    search_fields = ['brand']

    def queryAnnotate(self, brands):
        brands = brands.values('id', 'brand', 'enabled'). \
            annotate(type_item=F('type_item__kind'))
        return brands

    def list(self, request, company_pk, typeitem_pk):
        queryset_list = Brand.objects.filter(
            type_item=typeitem_pk,
            enabled=True
        ).order_by(Lower('brand'))
        query = self.request.GET.get("search")
        if query:
            queryset_list = queryset_list.filter(
                Q(brand__icontains=query)
            ).distinct()
        brands = self.queryAnnotate(queryset_list)
        return Response(brands)

    def retrieve(self, request, pk, company_pk, typeitem_pk):
        r_queryset = get_object_or_404(
            Brand,
            id=pk,
            type_item=typeitem_pk,
            enabled=True
        )
        serializer = BrandSerializer(r_queryset)
        return Response(serializer.data)

    def create(self, request, company_pk, typeitem_pk):
        """Este metodo se encuentra des-habilitado"""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        try:
            Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"company": ["Esa compañia no existe"]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            typeitem = TypeItem.objects.get(
                id=typeitem_pk, company__pk=company_pk)
        except ObjectDoesNotExist:
            return Response({"TypeItem": ["No existe ese tipo de objeto"]}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()

        serializer = BrandSerializer(data=data)
        if serializer.is_valid():
            serializer.validated_data['type_item'] = typeitem
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, company_pk, typeitem_pk, **kwargs):
        """Este metodo se encuentra des-habilitado"""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        data = request.data.copy()
        try:
            company = Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"company": "Esa compañia no existe"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            typeitem = Brand.objects.get(
                type_item=typeitem_pk, type_item__company=company_pk)
        except ObjectDoesNotExist:
            return Response({"item": "No existe el tipo de objeto"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BrandSerializer(brand, data=data)
        if serializer.is_valid():
            serializer.validated_data['company'] = company
            serializer.validated_data['type_item'] = typeitem
            serializer.save()
            return Response(request.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        def destroy(self, request, pk, company_pk, typeitem_pk,):
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class LostItemView(APIView):
    """
    En este endpoint se listan todos los objetos perdidos,

    """
    queryset = Item.objects.all()
    serializer_class = LostItemSerializer
    filter_backends = [SearchFilter]
    search_fields = ['owner_dni']
    permission_classes = [GuardAndSuperiorsOnly]

    def get_serializer_class(self):
        return self.serializer_class

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
        return Response(lost_items, status=status.HTTP_200_OK)
