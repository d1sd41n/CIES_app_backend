from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models.functions import Lower
from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
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
)

class auxViewSet(viewsets.ViewSet):
    """esta view es para los endpoints vacios que se usan para generar jerarquias,
    como items/company o items/compani/id/seats,
    aqui no se mostrará absolutamente nada"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializerList

class CompanyViewSet(viewsets.ModelViewSet):
    """
    Ejemplo URL:  http://localhost:8000/core/companies
    Si se esta en el list:
    Este end point lista todas las compañias en la bd
    se puede filtrar por nombre y nit de la compañia
     /?search=(parametro)

    Si se esta en el retrieve:
    desde aqui se edita la informacion y se elimina la compañia
     espesifica"""
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
                        Q(name__icontains=query)
                        ).distinct()
            serializer = CompanySerializerList(queryset_list, many=True)
            return Response(serializer.data)
        serializer = CompanySerializerList(queryset_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        """desde aqui se edita la informacion y se elimina la compañia
        espesifica"""
        r_queryset = get_object_or_404(
                    Company,
                    id=pk,
                    enabled=True
                    )
        serializer = CompanySerializerList(r_queryset)
        return Response(serializer.data)


class SeatViewSet(viewsets.ModelViewSet):
    """
    Ejemplo URL: http://localhost:8000/core/companies/1/seats
    -List: Lista todas las sedes de la compañia,
    cuando se hace un post para crear una sede no se debe especificar
    la compañia, el post automaticamente agrega la compañia en la cual se
    esta creando la sede.
    El address de la sede se agrega en otro endpoint.
    Se filtra por el campo name  /?search=(name).
    al hacer post se debe espesificar el id de la compañia de la sede
    en el JSON en el campo company.
    -Detail: muestra los detalles de una sede, permite editarla y eliminarla,


    """

    queryset = Seat.objects.all().order_by(Lower('name'))
    serializer_class = SeatSerializerList
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
    Ejemplo URL:  http://localhost:8000/core/companies/1/seats/1/users
    LIst:
    Este endpoint lista todos los usuarios de la sede.
    Solo lista el modelo User, no lista los datos de CustomUser,
    Sin embargo el metodo post de este endpoint llena ambos modelos
    User y CustomUser.

    Para hacer el post correctamente se deben incluir los datos tanto de User
    como CustomUser en el mismo JSON, ejemplo:
    <pre>
    {
    "is_superuser": false,
    "username": "BenitoKamelas",
    "first_name": "Benito",
    "last_name": "Kamelas",
    "email": "tukulito@dds.com",
    "is_staff": false,
    "is_active": false,
    "password": "ssdjdjd3333",
    "gender": "M",
    "nit": "666",
    "dni": "666"
    }
    </pre>

    Para filtrar ser usa ?search=(contenido), se puede buscar por
    nit, nombre de usario y correo, fisrt_name, last_name.
    <pre>
    ATENCION!
    #########################################################
    ESTE ENDPOINT ESTA INCOMPLETO


    Faltan permisos, peuden haber fallas de seguridad
    #########################################################


    para ver los datos del customUser ir al siguiente endpoint:

    http://localhost:8000/core/companies/id/seats/id/users/id/custom/
    </pre>"""
    queryset = User.objects.all().order_by(Lower('username'))
    serializer_class = UserSerializerList
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'email']

    def list(self, request, company_pk, seat_pk):
        queryset_list = User.objects.filter(
            customuser__seat=seat_pk,
            customuser__seat__company=company_pk
            ).order_by(Lower('username'))
        query = self.request.GET.get("search")
        if query:
            queryset_list = queryset_list.filter(
                        Q(username__icontains=query) |
                        Q(first_name__icontains=query) |
                        Q(last_name__icontains=query) |
                        Q(email__icontains=query)
                        ).distinct()
            serializer = UserSerializerList(queryset_list, many=True)
            return Response(serializer.data)
        serializer = UserSerializerList(queryset_list, many=True)
        return Response(serializer.data)

    def create(self, request, company_pk, seat_pk):
        serializer = UserSerializerList(data=request.data)
        if serializer.is_valid():
            seat = get_object_or_404(
                        Seat,
                        Q(id=seat_pk) &
                        Q(company=company_pk)
                        )
            serializer.save()
            id = serializer.data['id']
            user = User.objects.get(pk=id)
            request.data['user'] = user
            request.data['address'] = None
            customUser = CustomUser.objects.create_custom_user(request.data)
            SeatHasUser.objects.create(seat=seat, user=customUser)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk, company_pk, seat_pk):
        query = get_object_or_404(
                                User,
                                customuser__seat=seat_pk,
                                customuser__seat__company=company_pk,
                                id=pk
                                )
        serializer = UserSerializerDetail(query)
        return Response(serializer.data)


class SeatCustomUserDetail(generics.RetrieveUpdateDestroyAPIView):
    """Muestra los datos de customUser de determinado usuario,
    tambien desde aqui se puede editar."""

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
    """En esta Api se inserta, consulta, edita, elimina la direccion de determinada sede de la compañia,
    como al crearse la sede no se crea una address entonces este campo viene vasio y por tanto se debe llenar
    por aquí, si ya existe un adress y se vuelve a insertar otro, este nuevo reemplaza la address anterior sin
    eliminarla de la BD

    Aqui en el metodo get no hacemos la consulta directa a Locations para permitirnos mostrar dos mensajes diferentes,
    uno en caso que la jerarquia este incorrecta y otro en caso de que la sede aun no tenga direccion

    Al hacer post se debe mandar el id de la ciudad en la cual va a estar la direccion ejemplo  "city": 1"""
    queryset = Location.objects.all()
    serializer_class = AddressSerializer

    def retrieve(self, request, company_pk, seat_pk):
        queryset = get_object_or_404(
                    Seat,
                    id=seat_pk,
                    company=company_pk
                    ).address
        if(queryset is None):
            return Response({'address': 'This seat does not have address :('}, status=status.HTTP_404_NOT_FOUND)
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
    En este endpint se lsitan y se registran los visitantes
    de la compañia que registran sus items.


    La forma de registrar un visitante se hace con el siguiente JSON


    {
    "first_name": "umberto hannibal",
    "last_name": "Castrillon",
    "gender": "M",
    "dni": "5457767",
    "enabled": true
    }

    La compañia se añade automaticamente en la view

    """

    queryset = Visitor.objects.all().order_by(Lower('last_name'))
    serializer_class = VisitorSerializer
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['name']

    def list(self, request, company_pk):
        queryset_list = Visitor.objects.filter(
            company=company_pk,
            enabled=True
            ).order_by(
                Lower('last_name')
            )
        # query = self.request.GET.get("last_name")
        # if query:
        #     queryset_list = queryset_list.filter(
        #                 Q(name__icontains=query)
        #                 ).distinct()
            # serializer = VisitorSerializer(queryset_list, many=True)
            # return Response(serializer.data)
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
