from rest_framework import generics
from rest_framework import viewsets
from django.contrib.auth.models import Group
from rest_framework.response import Response
from django.db.models.functions import Lower
from django.db.models import Q
from django.db.models import F
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth.models import User
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import status
from ubication.models import Location
from core.models import (
    Company,
    Seat,
    CustomUser,
    Visitor,
    SeatHasUser,
)
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)
from core.serializers import (
    CompanySerializerList,
    SeatSerializerList,
    SeatSerializerDetail,
    UserSerializerList,
    UserSerializerDetail,
    CustomUserSerializer,
    AddressSerializer,
    VisitorSerializer,
    UserSerializerListCustom
)


class auxViewSet(viewsets.ViewSet):
    """Esta view es para los EndPoints vacíos
    que se usan para generar jerarquías,
    como items/company o items/compani/id/seats,
    aqui no se mostrará absolutamente nada"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializerList


class CompanyViewSet(viewsets.ModelViewSet):
    """
    Ejemplo URL:  http://localhost:8000/core/companies

    Si se consultan todas las compañías:
    El EndPoint listará todas las compañias en la BD,
    se puede filtrar por nombre y nit de la compañía de la siguiente forma
     '/?search=(parámetro)'

    Si se consulta una compañía en específico:
    desde aquí se edita la información y se elimina la compañía
    específica"""
    permission_classes = (DRYPermissions,)
    queryset = Company.objects.all().order_by(Lower('name'))
    serializer_class = CompanySerializerList
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nit', 'name']

    def list(self, request):
        queryset_list = Company.objects.filter(
            enabled=True
        )
        query = self.request.GET.get("search")
        if query:
            queryset_list = queryset_list.filter(
                        Q(name__icontains=query) |
                        Q(nit__icontains=query)
                        ).distinct()
            serializer = CompanySerializerList(queryset_list, many=True)
            return Response(serializer.data)
        serializer = CompanySerializerList(queryset_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        r_queryset = get_object_or_404(
                    Company,
                    id=pk,
                    enabled=True
                    )
        serializer = CompanySerializerList(r_queryset)
        return Response(serializer.data)


class SeatViewSet(viewsets.ModelViewSet):
    """
    Ejemplo URL: http://localhost:8000/core/companies/pk/seats

    -List: Lista todas las sedes de la compañia,
    cuando se hace un post para crear una sede no se debe especificar
    la compañia, el post automaticamente agrega la compañia en la cual se
    esta creando la sede.
    El address de la sede se agrega en otro endpoint.
    Para filtrar por el campo name  /?search=(name).
    -Detail: muestra los detalles de una sede, permite editarla y eliminarla,

    se filtra con el nombre de la sede
    """

    queryset = Seat.objects.all().order_by(Lower('name'))
    serializer_class = SeatSerializerList
    permission_classes = (DRYPermissions,)
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']

    def list(self, request, company_pk):
        queryset_list = Seat.objects.filter(
            company=company_pk,
            enabled=True
            ).order_by(
                Lower('name')
            )
        query = self.request.GET.get("search")
        if query:
            queryset_list = queryset_list.filter(
                        Q(name__icontains=query)
                        ).distinct()
            serializer = SeatSerializerList(queryset_list, many=True)
            return Response(serializer.data)
        serializer = SeatSerializerList(queryset_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, company_pk):
        r_queryset = get_object_or_404(
                    Seat,
                    id=pk,
                    company=company_pk,
                    enabled=True
                    )
        serializer = SeatSerializerDetail(r_queryset)
        return Response(serializer.data)


class SeatUserViewSet(viewsets.ModelViewSet):
    """
    Ejemplo URL:  http://localhost:8000/core/companies/pk/seats/pk/users
    List:
    Este endpoint lista todos los usuarios de la sede.
    Solo lista el modelo User, no lista los datos de CustomUser,
    Sin embargo el metodo post de este endpoint llena ambos modelos
    User y CustomUser.

    Para hacer el post correctamente se deben incluir los datos tanto de User
    como CustomUser en el mismo JSON, ejemplo:

    <pre>
    {
    "is_superuser": true/false,  # true si es un super usuario, false si no
    "username": "Test_username",  # Nombre de usuario, como una string
    "first_name": "test_name",  # Primer nombre del usuario, como una string
    "last_name": "test_lastname",  # Apellido del usuario, como una string
    "email": "testemail@testserver.test",  # E-mail del usuario
    "is_staff": true/false,  # true si el usuario es staff, false si no
    "is_active": true/false,  # true si el usuario está activo, false  si no
    "password": "testpassword",  # La contraseña del usuario, como una string
    "type": "guard", # Tipo de usuario si es un guardia o es administrador (###nombre de grupos todavia no definidos#####)
    "dni": "test_dni"  # El número de identidad del usuario, como una string
    }
    </pre>

    El siguiente json lo uso para test (mientras estamos en desarrollo), porfavor no me lo borren...
    <pre>
    {
    "is_superuser": false,
    "username": "farolito",
    "first_name": "prp",
    "last_name": "psps",
    "email": "q@l.com",
    "password": "testpassword",
    "type": "guard",
    "dni": "test_dni"
    }
    </pre>

    Para filtrar ser usa ?search=(contenido), se puede buscar por
    DNI, nombre de usario, correo, nombre o apellido.

    para editar los datos del customUser ir al siguiente endpoint:

    http://localhost:8000/core/companies/id/seats/id/users/id/custom/
    """
    queryset = User.objects.all().order_by(Lower('username'))
    permission_classes = (DRYPermissions,)
    serializer_class = CustomUserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'email', 'dni']

    def queryAnnotate(self, users):
        # print(user.groups.all())
        users = users \
                    .values('id', 'dni',) \
                    .annotate(last_login=F('user__last_login'),
                              is_superuser=F('user__is_superuser'),
                              username=F('user__username'),
                              first_name=F('user__first_name'),
                              last_name=F('user__last_name'),
                              email=F('user__email'),
                              is_staff=F('user__is_staff'),
                              is_active=F('user__is_active'),
                              date_joined=F('user__date_joined'),
                              type=F('user__groups'))
        return users

    def list(self, request, company_pk, seat_pk):
        queryset_list = CustomUser.objects.filter(
            seat=seat_pk,
            seat__company=company_pk
            ).order_by(Lower('user__username'))
        users = self.queryAnnotate(queryset_list)
        query = self.request.GET.get("search")
        if query:
            queryset_list = queryset_list.filter(
                        Q(user__username__icontains=query) |
                        Q(user__first_name__icontains=query) |
                        Q(user__last_name__icontains=query) |
                        Q(user__email__icontains=query) |
                        Q(dni__icontains=query)
                        ).distinct()
        users = self.queryAnnotate(queryset_list)
        serializer = UserSerializerListCustom(users, many=True)
        return Response(serializer.data)

    def create(self, request, company_pk, seat_pk):
        serializer_user = UserSerializerList(data=request.data)
        serializer_custom = UserSerializerList(data=request.data)
        if serializer_custom.is_valid() and serializer_user.is_valid() and request.data["type"] != "Developer":
            # Aqui verificamos la existencia de la sede, compañia y grupo
            seat = get_object_or_404(
                        Seat,
                        Q(id=seat_pk) &
                        Q(company=company_pk)
                        )
            group = get_object_or_404(
                        Group,
                        name=request.data["type"]
                        )
            user = serializer_user.save()
            request.data['user'] = user
            customUser = CustomUser.objects.create_custom_user(request.data)
            SeatHasUser.objects.create(seat=seat, user=customUser)
            group.user_set.add(user)
            return Response(request.data, status=status.HTTP_201_CREATED)
        return Response({"Error": "Datos ingresados de forma incorrecta"}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk, company_pk, seat_pk):
        user = CustomUser.objects.filter(seat__company__id=company_pk,
                                         seat__id=seat_pk, id=pk)
        if (not len(user)):
            return Response(status=status.HTTP_404_NOT_FOUND)
        checks = self.queryAnnotate(user)
        serializer = UserSerializerListCustom(checks, many=True)
        return Response(serializer.data)


class SeatCustomUserDetail(generics.RetrieveUpdateDestroyAPIView):
    """Muestra los datos de customUser de determinado usuario,
    tambien desde aqui se puede editar."""
    permission_classes = (DRYPermissions,)
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def retrieve(self, request, company_pk, seat_pk, user_pk):
        r_queryset = get_object_or_404(
                    CustomUser,
                    user=user_pk,
                    seat=seat_pk,
                    seat__company=company_pk
                    )
        serializer = CustomUserSerializer(r_queryset)
        return Response(serializer.data)

    def put(self, request, company_pk, seat_pk, user_pk):
        custom = get_object_or_404(
                    CustomUser,
                    user=user_pk,
                    seat=seat_pk,
                    seat__company=company_pk
                    )
        serializer = CustomUserSerializer(custom, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, company_pk, seat_pk, user_pk):
        custom = get_object_or_404(
                    CustomUser,
                    user=user_pk,
                    seat=seat_pk,
                    seat__company=company_pk
                    )
        serializer = CustomUserSerializer(custom, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SeatAddress(generics.RetrieveUpdateDestroyAPIView,
                  generics.CreateAPIView):
    """En esta Api se inserta, consulta, edita y elimina la
    dirección de determinada sede de la compañía,
    al crearse la sede no se crea una address por lo cual este campo
    queda vacío y se debe llenar por este EndPoint,
    si ya existe una dirección y se vuelve a insertar otra,
    esta nueva reemplazará la anterior sin eliminarla de la BD.

    En el metodo GET no se realiza una consulta directa a Locations para
    permitir mostrar dos mensajes diferentes, uno en caso que la jerarquía
    este incorrecta y otro en caso de que la sede aún no tenga dirección.

    Al hacer post se debe mandar el Id de la ciudad en la cual va a
    estar la dirección ejemplo  "city": 1"""
    permission_classes = (DRYPermissions,)
    queryset = Location.objects.all()
    serializer_class = AddressSerializer

    def retrieve(self, request, company_pk, seat_pk):
        queryset = get_object_or_404(
                    Seat,
                    id=seat_pk,
                    company=company_pk
                    ).address
        if(queryset is None):
            return Response({'address': 'This seat does not have address :('},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = AddressSerializer(queryset)
        return Response(serializer.data)

    def post(self, request, company_pk, seat_pk):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            id = serializer.data['id']
            seat = get_object_or_404(
                        Seat,
                        id=seat_pk,
                        company=company_pk
                        )
            seat.address = Location.objects.get(id=id)
            seat.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, company_pk, seat_pk):
        address = get_object_or_404(
                    Location,
                    seat=seat_pk,
                    seat__company=company_pk
                    )
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, company_pk, seat_pk):
        address = get_object_or_404(
                    Location,
                    seat=seat_pk,
                    seat__company=company_pk
                    )
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request,  company_pk, seat_pk):
        address = get_object_or_404(
                    Location,
                    seat__company=company_pk,
                    seat=seat_pk
                    )
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompanyVisitor(viewsets.ModelViewSet):
    """
    En este EndPoint se listan y registran los visitantes
    de la compañia que han registrado objetos.


    La forma de registrar un visitante se hace con el siguiente JSON

    {
    "first_name": "Test_name",  # Primer nombre, como una string
    "last_name": "Test_lastname",  # Segundo nombre, como una string
    "dni": "Test_dni",  # Número de identidad, como una string
    'email': "email@company.com" # email del visitante
    "enabled": true/false  # true si está habilitado, false si no
    }

    La compañía se añade automaticamente en la view
    """

    permission_classes = (DRYPermissions,)
    queryset = Visitor.objects.all().order_by(Lower('last_name'))
    serializer_class = VisitorSerializer
    filter_backends = [SearchFilter]
    search_fields = ['dni']

    def list(self, request, company_pk):
        queryset_list = Visitor.objects.filter(
            company=company_pk,
            enabled=True
            ).order_by(
                Lower('last_name')
            )
        query = self.request.GET.get("search")
        if query:
            queryset_list = Visitor.objects.filter(
                        Q(dni__iexact=query)
                        ).distinct()
        serializer = VisitorSerializer(queryset_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, company_pk):
        r_queryset = get_object_or_404(
                    Visitor,
                    id=pk,
                    company=company_pk,
                    enabled=True
                    )
        serializer = VisitorSerializer(r_queryset)
        return Response(serializer.data)

    def create(self, request, company_pk):
        data = request.data.copy()
        data["company"] = company_pk
        serializer = VisitorSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
