from rest_framework import generics
from rest_framework import viewsets
from django.core.exceptions import ObjectDoesNotExist
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
from ubication.serializers import LocationSerializer
from core.models import (
    Company,
    Seat,
    CustomUser,
    Visitor,
)
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)
from core.serializers import (
    CompanySerializer,
    SeatSerializer,
    SeatSerializerList,
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
    serializer_class = CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """
    Ejemplo URL:  http://localhost:8000/core/companies

    create:
    ejemplo de json para crear una compañia
    <pre>
    {
    "nit": "723",
    "name": "company1",
    "email": "qd@p.com",
    "website": "https://www.company.com"
    }
    </pre>

    Si se consultan todas las compañías:
    El EndPoint listará todas las compañias en la BD,
    se puede filtrar por nombre y nit de la compañía de la siguiente forma
     '/?search=(parámetro)'

    Si se consulta una compañía en específico:
    desde aquí se edita la información y se elimina la compañía
    específica"""
    permission_classes = (DRYPermissions,)
    queryset = Company.objects.all().order_by(Lower('name'))
    serializer_class = CompanySerializer
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
            serializer = CompanySerializer(queryset_list, many=True)
            return Response(serializer.data)
        serializer = CompanySerializer(queryset_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        r_queryset = get_object_or_404(
                    Company,
                    id=pk,
                    enabled=True
                    )
        serializer = CompanySerializer(r_queryset)
        return Response(serializer.data)


class SeatViewSet(viewsets.ModelViewSet):
    """
    Ejemplo URL: http://localhost:8000/core/companies/pk/seats

    ejemplo de JSON:

    -create: se deben añadir campos basicos de sede, el id de la ciudad
    donde esta ubicada la cede y la direccion de la sede. La compañia se añade
    automaticamente basandose en la jerarquia.
    ejemplo:
    <pre>
    {
    "email": "qww@email.com",
    "name": "sede1",
    "address": "calle 3 carrera 7",
    "city": 1
    }
    </pre>

    -List: Lista todas las sedes de la compañia,
    cuando se hace un post para crear una sede no se debe especificar
    la compañia, el post automaticamente agrega la compañia en la cual se
    esta creando la sede.
    """

    queryset = Seat.objects.all().order_by(Lower('name'))
    serializer_class = SeatSerializer
    permission_classes = (DRYPermissions,)
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']

    def queryAnnotate(self, seats):
        seats = seats \
                    .values('id','email','name') \
                    .annotate(address=F('address__address'),
                              company=F('company__name'))
        return seats

    def create(self, request, company_pk):
        data = request.data.copy()
        data['company'] = company_pk
        try:
            Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": "compañia incorrecta"}, status=status.HTTP_400_BAD_REQUEST)
        serializer_seat = SeatSerializer(data=data)
        serializer_address = LocationSerializer(data=data)
        if serializer_address.is_valid():
            adress = serializer_address.save()
            data["address"] = adress.id
            if serializer_seat.is_valid():
                serializer_seat.save()
                return Response(request.data, status=status.HTTP_201_CREATED)
            else:
                adress.delete()
                return Response(serializer_seat.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_address.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, company_pk):
        queryset_list = Seat.objects.filter(
            company=company_pk,
            enabled=True
            ).order_by(
                Lower('name')
            )
        seats = self.queryAnnotate(queryset_list)
        serializer = SeatSerializerList(seats, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, company_pk):
        seat = Seat.objects.filter(company__id=company_pk, id=pk)
        if (not len(seat)):
            return Response(status=status.HTTP_404_NOT_FOUND)
        seat = self.queryAnnotate(seat)
        serializer = SeatSerializerList(seat, many=True)
        return Response(serializer.data)

    def update(self, request, pk, company_pk, **kwargs):
        data = request.data.copy()
        data['company'] = company_pk
        seat = get_object_or_404(
                    Seat,
                    id=pk,
                    company=company_pk
                    )
        location = get_object_or_404(
                    Location,
                    id=seat.address.id
                    )
        address = data['address']
        data['address'] = seat.address.id
        serializer_seat = SeatSerializer(seat, data=data)
        if serializer_seat.is_valid():
            location.address = address
            location.save()
            serializer_seat.save()
            return Response(request.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer_seat.errors, status=status.HTTP_400_BAD_REQUEST)


class SeatUserViewSet(viewsets.ModelViewSet):
    """
    Ejemplo URL:  http://localhost:8000/core/companies/pk/seats/pk/users
    List:
    Este endpoint gestiona usuarios de una sede.

    Para hacer el post correctamente se deben incluir los datos tanto de User
    como CustomUser  y un campo adicional llamado "type" el cual
    es el rol del usuario guardia o administrador ####(nombre de los roles sin definir todavia)###

    JSON para post o put(en este caso modificando los campos que se van a cambiar), ejemplo:

    <pre>
    {
    "username": "Test_username",  # Nombre de usuario, como una string
    "first_name": "test_name",  # Primer nombre del usuario, como una string
    "last_name": "test_lastname",  # Apellido del usuario, como una string
    "email": "testemail@testserver.test",  # E-mail del usuario
    "password": "testpassword",  # La contraseña del usuario, como una string
    "type": "guard", # Tipo de usuario si es un guardia o es administrador (###nombre de grupos todavia no definidos#####)
    "dni": "test_dni"  # El número de identidad del usuario, como una string
    }
    </pre>

    El siguiente json lo uso para test (mientras estamos en desarrollo), porfavor no me lo borren...
    <pre>
    {
    "username": "user2",
    "first_name": "name",
    "last_name": "lastname",
    "email": "q@l.com",
    "password": "testpassword",
    "type": "guard",
    "dni": "test_dni"
    }
    </pre>

    Para filtrar ser usa ?search=(contenido), se puede buscar por
    DNI, nombre de usario, correo, nombre o apellido.
    """
    queryset = User.objects.all().order_by(Lower('username'))
    permission_classes = (DRYPermissions,)
    serializer_class = CustomUserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'email', 'dni']

    def queryAnnotate(self, users):
        users = users \
                    .values('dni',) \
                    .annotate(last_login=F('user__last_login'),
                              is_superuser=F('user__is_superuser'),
                              username=F('user__username'),
                              first_name=F('user__first_name'),
                              last_name=F('user__last_name'),
                              email=F('user__email'),
                              is_staff=F('user__is_staff'),
                              is_active=F('user__is_active'),
                              date_joined=F('user__date_joined'),
                              type=F('user__groups'),
                              id=F('user__id'))
        return users

    def list(self, request, company_pk, seat_pk):
        queryset_list = CustomUser.objects.filter(
            seat=seat_pk,
            seat__company=company_pk
            ).order_by(Lower('user__username'))
        users = self.queryAnnotate(queryset_list)
        serializer = UserSerializerListCustom(users, many=True)
        return Response(serializer.data)

    def create(self, request, company_pk, seat_pk):
        data = request.data.copy()
        data["is_superuser"] = False
        data["is_staff"] = False
        data["is_active"] = True
        data["seat"] = seat_pk


        # verificasion de campos externos
        try:
            data['type']
        except KeyError:
            return Response({"Error": "falta el campo type"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            group = Group.objects.get(name=data["type"])
        except ObjectDoesNotExist:
            return Response({"Error": "el campo type es incorrecto"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Seat.objects.get(id=seat_pk, company__id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": "sede incorrecta"}, status=status.HTTP_400_BAD_REQUEST)
        if data["type"] == "Developer":
            return Response({"Error": "Tipo de usuario no permitido"}, status=status.HTTP_400_BAD_REQUEST)


        serializer_user = UserSerializerList(data=data)
        serializer_custom = CustomUserSerializer(data=data)
        if serializer_user.is_valid():
            user = serializer_user.save()
            data['user'] = user.id
            if serializer_custom.is_valid():
                customUser = serializer_custom.save()
                group.user_set.add(user)
                data = request.data.copy()
                data.pop("password")
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                user.delete()
                return Response(serializer_custom.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_user.errors, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk, company_pk, seat_pk):
        user = CustomUser.objects.filter(seat__company__id=company_pk,
                                         seat__id=seat_pk, user__id=pk)
        if (not len(user)):
            return Response(status=status.HTTP_404_NOT_FOUND)
        checks = self.queryAnnotate(user)
        serializer = UserSerializerListCustom(checks, many=True)
        return Response(serializer.data)

    def destroy(self, request, pk, company_pk, seat_pk, **kwargs):
        user = get_object_or_404(
                    User,
                    id=pk,
                    )
        custom = get_object_or_404(
                    CustomUser,
                    user=user.id,
                    seat=seat_pk,
                    seat__company=company_pk
                    )
        user.delete()
        return Response({"Delete": "Done"}, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk, company_pk, seat_pk, **kwargs):
        data = request.data.copy()
        # validadores
        if data["type"] == "Developer":
            return Response({"Error": "Tipo de usuario no permitido"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            group = Group.objects.get(name=data["type"])
        except ObjectDoesNotExist:
            return Response({"Error": "el campo type es incorrecto"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Seat.objects.get(id=seat_pk, company__id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": "sede incorrecta"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data['type']
        except KeyError:
            return Response({"Error": "Falta tipo de usuario"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({"Error": "User incorrecto"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            custom = CustomUser.objects.get(user=user.id, seat=seat_pk, seat__company=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": "No se pudo encontrar el Customuser del user"}, status=status.HTTP_400_BAD_REQUEST)

        data["is_superuser"] = False
        data["is_staff"] = False
        data["is_active"] = True
        data["seat"] = seat_pk
        data['user'] = user.id
        serializer_user = UserSerializerList(user, data=data)
        serializer_custom = CustomUserSerializer(custom, data=data)
        if serializer_user.is_valid(): #and serializer_custom.is_valid():
            if serializer_custom.is_valid():
                serializer_user.save()
                serializer_custom.save()
                user.groups.clear()
                group.user_set.add(user)
                # data = request.data.copy()
                # data.pop("password")
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer_custom.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_user.errors, status=status.HTTP_400_BAD_REQUEST)




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
