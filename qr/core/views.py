from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Company, CustomUser, Seat, Visitor
from core.serializers import (AddressSerializer, CompanySerializer,
                              CustomUserSerializer, SeatSerializer,
                              SeatSerializerList, UserSerializer,
                              UserSerializerEdit, UserSerializerListCustom,
                              VisitorSerializer, VisitorExistSerializer)
from ubication.models import Location
from ubication.serializers import LocationSerializer
from qr.permissions import (DeveloperOnly, ManagerAndSuperiorsOnly,
                            SupervisorAndSuperiorsOnly, GuardAndSuperiorsOnly)

import datetime
from core.authentication import UserLoginRateThrottle


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
    queryset = Company.objects.all().order_by(Lower('name'))
    permission_classes = [DeveloperOnly]
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

    def destroy(self, request, pk):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class SeatViewSet(viewsets.ModelViewSet):
    """
    Ejemplo URL: http://localhost:8000/core/companies/pk/seats

    -CREATE-POST:
    *se deben añadir los campos basicos de sede, el id de la ciudad
    donde esta ubicada la cede y la direccion de la sede.
    *La COMPAÑIA se añade AUTOMATICAMENTE basandose en la jerarquia, extrayendo el id de la URL,
    si de todas formas se inserta compañia en el JSON ese campo será ignorado y no se hará nada con el.
    *el campo city se usa para crear la tabla de la direccion de la sede, ese campo no pertenece a sede.
    *solo se usaran los campos necesarios para crear la sede, si se pasa informacion de mas en el
    JSON, esos datos seran ignorados e igualmente se creara la sede usando solo los campos necesarios
    (si la sintaxis del JSON es correcta y los campos que son necesarios tambien lo son).
    *Si la sede se crea correctamente la respuesta devuelve el MISMO JSON que se inserto,
    mostrando toda la informacion de la sede incluyendo informacion no reelevante(no sera usada tal
    cual se menciona en el punto anterior), al consultar la sede con el GET,
    la informacion ireelevante no aparecera ya que no existe ni la informacion que esta en modo solo
    escritura.

    ejemplo:
    <pre>
    {
    "email": "qww@email.com",
    "name": "sede1",
    "address": "calle 3 carrera 7",
    "city": 1
    }
    </pre>

    -EDIT-PUT/PATCH:
    *Al modificar una sede existente se deben pasar todos los campos de la sede(**"exepto compañia"**) mas la
    direccion de esa sede, los campos que no se van a cambiar se deben enviar igualmente (con la misma informacion que ya tienen)
    y los que se van a cambiar con la informacion nueva.
    *al igual que en create, solo se usaran los campos de la sede mas direccion, si se pasa informacion de mas en el
    JSON, esos datos seran ignorados e igualmente se modificara la sede usando solo los campos necesarios
    (si la sintaxis del JSON es correcta y los campos que son necesarios tambien lo son).
    *Si la sede se modifica la respuesta devuelve el MISMO JSON que se inserto,
    mostrando toda la informacion de la sede incluyendo informacion no reelevante(no sera usada tal
    cual se menciona en el punto anterior), al consultar la sede con el GET,
    la informacion ireelevante no aparecera ya que no existe ni la informacion que esta en modo solo
    escritura.
    *compañia se extrae de la URL al igual que en create.
    ejemplo json en edit:
    {
    "id": "8",
    "name": "Nuevo nombre sede1",
    "address": "calle 55 carrera 7",
    "email": "email@email.com"
    }
    """

    queryset = Seat.objects.all().order_by(Lower('name'))
    permission_classes = [DeveloperOnly]
    serializer_class = SeatSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']

    def queryAnnotate(self, seats):
        seats = seats \
            .values('id', 'email', 'name') \
            .annotate(address=F('address__address'),
                      company=F('company__name'))
        return seats

    def create(self, request, company_pk):
        data = request.data.copy()
        data['company'] = company_pk
        try:
            Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": "compañía incorrecta"}, status=status.HTTP_400_BAD_REQUEST)
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
                return Response({"Error": serializer_seat.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": serializer_address.errors}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"Error": serializer_seat.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk, company_pk, ):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class SeatUserViewSet(viewsets.ModelViewSet):
    """
    Ejemplo URL:  http://localhost:8000/core/companies/pk/seats/pk/users
    -GET-lIST:
    *la id que aparece es del modelo USER
    *el password no aparece listado.

    -CREATE-POST:
    *se deben añadir los campos basicos de USER mas el campo DNI de customuser y el tipo grupo al que pertenecer (type).
    *La COMPAÑIA y SEDE se añaden AUTOMATICAMENTE basandose en la jerarquia, extrayendo el id de la URL,
    y sede, si de todas formas se inserta compañia o sede en el JSON esos campos seran ignorados
    y no se hara nada con ellos.
    *solo se usaran los campos necesarios para crear el usuario, si se pasa informacion de mas en el
    JSON, esos datos seran ignorados e igualmente se creara el usuario y su customuser usando solo los campos necesarios
    (si la sintaxis del JSON es correcta y los campos que son necesarios tambien lo son).
    *Si la sede se crea correctamente se devuelve el MISMO JSON que se inserto,
    mostrando toda la informacion tal cual exepto la contraceña, si se insertaron campos irrelevantes
    se mostraran en la respuesta a pesar de que no se hace nada con ellos.

    ejemplo del JSON:
    <pre>
    {
    "username": "user__last_name",
    "first_name": "name",
    "last_name": "lastname",
    "email": "q@l.com",
    "password": "testpassword",
    "type": "guard",
    "dni": "test_dni"
    }
    </pre>

    -EDIT-PUT/PATCH:
    *Al modificar un usuario existente se deben pasar todos los campos del usuario
     los campos que no se van a cambiar se deben enviar igualmente con la misma informacion que ya tienen
     exepto PASSWORD.
    *el campo password solo se debe agregar al JSON si la contraceña se va a modificar, si es es el verificasion
    se agrega el campo password al JSON no la nueva contraceña del usuario.
    *Si la contraceña no se va a cambiar NO DEBE HABER CAMPO PASSWORD en el JSON.

    ejemplo JSON modificando password:
    <pre>
    {
    "username": "user9",
    "first_name": "name",
    "last_name": "lastname",
    "dni": "43433tt",
    "password": "contraceña23324234hd",
    "email": "es@sd.com",
    "type": "guard"
    }
    </pre>

    ejemplo JSON sin modificar password:
    <pre>
    {
    "username": "user9",
    "first_name": "name",
    "last_name": "lastname",
    "dni": "43433tt",
    "email": "es@sd.com",
    "type": "guard"
    }
    </pre>

    Para filtrar ser usa ?search=(contenido), se puede buscar por
    DNI, nombre de usario, correo, nombre o apellido.
    """
    queryset = User.objects.all().order_by(Lower('username'))
    permission_classes = [SupervisorAndSuperiorsOnly]
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
                      type=F('user__groups__name'),
                      id=F('user__id'))
        return users

    def list(self, request, company_pk, seat_pk):
        queryset_list = CustomUser.objects.filter(
            seat=seat_pk,
            seat__company=company_pk,
            user__is_active=True
        ).order_by(Lower('user__username'))
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
        data = request.data.copy()
        data["is_superuser"] = False
        data["is_staff"] = False
        data["is_active"] = True
        data["seat"] = seat_pk

        # verificasion de campos externos
        try:
            data['type']
        except KeyError:
            return Response({"Error": {'type': "el JSON no tiene el campo type"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            group = Group.objects.get(name=data["type"])
        except ObjectDoesNotExist:
            return Response({"Error": {'type': "no existe ese tipo de usuario"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Seat.objects.get(id=seat_pk, company__id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"seat": "sede incorrecta"}}, status=status.HTTP_400_BAD_REQUEST)
        if data["type"] == "Developer" or data["type"] == "Manager":
            return Response({"Error": {"type": "ese tipo de usuario no permitido"}}, status=status.HTTP_400_BAD_REQUEST)
        if not data["dni"].isnumeric():
            return Response({"Error": {"dni": "La Cedula solo puede ser numerica"}}, status=status.HTTP_400_BAD_REQUEST)

        serializer_user = UserSerializer(data=data)
        serializer_custom = CustomUserSerializer(data=data)
        if serializer_user.is_valid():
            user = serializer_user.save()
            try:  # password validator
                validate_password(data['password'], user)
            except ValidationError as e:
                user.delete()
                return Response({"Error": {"password": e}}, status=status.HTTP_400_BAD_REQUEST)
            user.password = make_password(data['password'])
            user.save()
            if serializer_custom.is_valid():
                customUser = serializer_custom.save()
                group.user_set.add(user)
                data = request.data.copy()
                data.pop("password")
                data['id'] = user.id
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                user.delete()
                return Response({"Error": serializer_custom.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": serializer_user.errors}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk, company_pk, seat_pk):
        user = CustomUser.objects.filter(seat__company__id=company_pk,
                                         seat__id=seat_pk, user__id=pk)
        if (not len(user)):
            return Response(status=status.HTTP_404_NOT_FOUND)
        checks = self.queryAnnotate(user)
        serializer = UserSerializerListCustom(checks, many=True)
        return Response(serializer.data)

    def destroy(self, request, pk, company_pk, seat_pk):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, pk, company_pk, seat_pk, **kwargs):
        data = request.data.copy()
        # validadores
        try:
            data['type']
        except KeyError:
            return Response({"Error": {'type': "el JSON no tiene el campo type"}}, status=status.HTTP_400_BAD_REQUEST)
        if data["type"] == "Developer":
            return Response({"Error": {"type": "ese tipo de usuario no permitido"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            group = Group.objects.get(name=data["type"])
        except ObjectDoesNotExist:
            return Response({"Error": {'type': "no existe ese tipo de usuario"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Seat.objects.get(id=seat_pk, company__id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"seat": "sede incorrecta"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"pk": "ese usuario no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            custom = CustomUser.objects.get(
                user=user.id, seat=seat_pk, seat__company=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"user": "No se pudo encontrar el Customuser del user"}}, status=status.HTTP_400_BAD_REQUEST)
        if not data["dni"].isnumeric():
            return Response({"Error": {"dni": "La Cedula solo puede ser numerica"}}, status=status.HTTP_400_BAD_REQUEST)
        # if data["type"] == "Manager" and user.groups.all()[0].name != "Manager":
        #     return Response({"Error": {"type": "No se agregar ese tipo de usuario a ese determinado usuario"}}, status=status.HTTP_400_BAD_REQUEST)


        data["is_superuser"] = False
        data["is_staff"] = False
        data["is_active"] = True
        data["seat"] = seat_pk
        data["user"] = user.id
        data.pop("last_login", None)

        # verificasion si hay contraceñas(si se va a cambiar la pass)
        pval = True
        try:
            data['password']
        except KeyError:
            pval = False


        serializer_user = UserSerializerEdit(user, data=data)
        serializer_custom = CustomUserSerializer(custom, data=data)
        if serializer_user.is_valid():  # and serializer_custom.is_valid():
            if serializer_custom.is_valid():
                if pval:
                    try:  # password validator
                        validate_password(data['password'], user)
                    except ValidationError as e:
                        return Response({"Error": {"password": e}}, status=status.HTTP_400_BAD_REQUEST)
                serializer_user.save()
                serializer_custom.save()
                if pval:
                    user.password = make_password(data['password'])
                    user.save()
                user.groups.clear()
                group.user_set.add(user)
                data = request.data.copy()
                if pval:
                    data.pop("password")
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                return Response({"Error": serializer_custom.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": serializer_user.errors}, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, pk, company_pk, seat_pk, **kwargs):
        data = request.data.copy()
        # validadores

        if 'type' in data:
            if data["type"] == "Developer":
                return Response({"Error": {"type": "ese tipo de usuario no permitido"}}, status=status.HTTP_400_BAD_REQUEST)
            try:
                group = Group.objects.get(name=data["type"])
            except ObjectDoesNotExist:
                return Response({"Error": {'type': "no existe ese tipo de usuario"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Seat.objects.get(id=seat_pk, company__id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"seat": "sede incorrecta"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"pk": "ese usuario no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            custom = CustomUser.objects.get(
                user=user.id, seat=seat_pk, seat__company=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"user": "No se pudo encontrar el Customuser del user"}}, status=status.HTTP_400_BAD_REQUEST)
        if 'dni' in data:
            if not data["dni"].isnumeric():
                return Response({"Error": {"dni": "La Cedula solo puede ser numerica"}}, status=status.HTTP_400_BAD_REQUEST)
        # if data["type"] == "Manager" and user.groups.all()[0].name != "Manager":
        #     return Response({"Error": {"type": "No se agregar ese tipo de usuario a ese determinado usuario"}}, status=status.HTTP_400_BAD_REQUEST)


        data["is_superuser"] = False
        data["is_staff"] = False
        data["is_active"] = True
        data["seat"] = seat_pk
        data["user"] = user.id
        data.pop("last_login", None)

        # verificasion si hay contraceñas(si se va a cambiar la pass)
        pval = True
        try:
            data['password']
        except KeyError:
            pval = False

        serializer_user = UserSerializerEdit(user, data=data, partial=True)
        serializer_custom = CustomUserSerializer(custom, data=data, partial=True)
        if serializer_user.is_valid():  # and serializer_custom.is_valid():
            if serializer_custom.is_valid():
                if pval:
                    try:  # password validator
                        validate_password(data['password'], user)
                    except ValidationError as e:
                        return Response({"Error": {"password": e}}, status=status.HTTP_400_BAD_REQUEST)
                serializer_user.save()
                serializer_custom.save()
                if pval:
                    user.password = make_password(data['password'])
                    user.save()
                if 'type' in data:
                    user.groups.clear()
                    group.user_set.add(user)
                data = request.data.copy()
                if pval:
                    data.pop("password")
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                return Response({"Error": serializer_custom.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": serializer_user.errors}, status=status.HTTP_400_BAD_REQUEST)


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

    queryset = Visitor.objects.all().order_by(Lower('last_name'))
    permission_classes = [GuardAndSuperiorsOnly,]
    serializer_class = VisitorSerializer
    filter_backends = [SearchFilter]
    search_fields = ['dni']

    def list(self, request, company_pk):

        queryset_list = Visitor.objects.filter(
            enabled=True,
            company__pk=company_pk
        ).order_by(
            Lower('last_name')
        )
        query = self.request.GET.get("search")
        if query:
            queryset_list = queryset_list.filter(
                Q(dni__iexact=query)
            ).distinct()
        serializer = VisitorSerializer(queryset_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, company_pk):
        r_queryset = get_object_or_404(
            Visitor,
            id=pk,
            company__pk=company_pk,
            enabled=True
        )
        serializer = VisitorSerializer(r_queryset)
        return Response(serializer.data)

    def create(self, request, company_pk, **kwargs):
        data = request.data.copy()
        try:
            company = Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"company": "la compañia no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        seat_registration = CustomUser.objects.get(user=request.user.pk).seat.pk
        data['seat_registration'] = seat_registration
        data['registered_by'] = request.user.pk
        serializer = VisitorSerializer(data=data)
        if serializer.is_valid():
            visitor_obj = serializer.save()
            visitor_obj.company.add(company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"Error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, company_pk, **kwargs):
        data = request.data.copy()
        data.pop("id", None)
        data.pop("registration_date", None)
        data.pop("seat_registration", None)
        data.pop("registered_by", None)
        try:
            company = Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"company": "la compañia no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            visitor = Visitor.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({"Error": "el visitante no existe"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = VisitorSerializer(visitor, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk, company_pk, **kwargs):
        data = request.data.copy()
        data.pop("id", None)
        data.pop("registration_date", None)
        data.pop("seat_registration", None)
        data.pop("registered_by", None)
        try:
            company = Company.objects.get(id=company_pk)
        except ObjectDoesNotExist:
            return Response({"Error": {"company": "la compañia no existe"}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            visitor = Visitor.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({"Error": "el visitante no existe"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = VisitorSerializer(visitor, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk, company_pk, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ObtainExpiringAuthToken(ObtainAuthToken):
    throttle_classes = (UserLoginRateThrottle,)

    def post(self, request):

        # Email auth
        data = request.data.copy()
        username = data["username"]
        try:
            username = User.objects.get(Q(username=username) | Q(email=username)).username
        except ObjectDoesNotExist:
            return Response({"non_field_errors": [
        "No puede iniciar sesión con las credenciales proporcionadas."
    ]}, status=status.HTTP_400_BAD_REQUEST)
        data["username"] = username


        serializer = self.serializer_class(data=data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created =  Token.objects.get_or_create(user=user)
        if not created:
                # update the created time of the token to keep it valid
                token.created = datetime.datetime.utcnow()
                token.save()
        custom = CustomUser.objects.get(user=user.pk)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'dni': custom.dni,
            'name': user.first_name,
            'last_name': user.last_name,
            'company': custom.seat.company_id,
            'seat': custom.seat_id,
        })


class VisitorExist(APIView):
    """
    Esta view es solo para consultar la existencia de un visistante en la
    base de datos.

    devuelve True si existe si no False.

    se debe enviar un json con el dni del visistante a consultar:

    {
    "first_name": "otro visistnte compañia 1",
    "last_name": "ssffds",
    "dni": "s44gdds",
    "email": "esil@company.com",
    "enabled": true
    }
    """
    permission_classes = (GuardAndSuperiorsOnly,)

    def post(self, request, company_pk):
        try:
            visitor = Visitor.objects.get(dni=request.data['dni'])
        except ObjectDoesNotExist:
            return Response({"exist": False,}, status=status.HTTP_200_OK)
        return Response({"exist": True,}, status=status.HTTP_200_OK)
