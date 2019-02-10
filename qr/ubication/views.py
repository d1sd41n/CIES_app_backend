from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.response import Response
from ubication.models import Country, Province, City
from qr.permissions import DeveloperOnly

from ubication.serializers import (
    CountrySerializer,
    ProvinceSerializer,
    CitySerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    """
    create:
    ejemplo de json:
    <pre>
    {
    "name": "pais3",
    "postalcode": "651"
    }
    </pre>
    list:
    Filtra por name y postalcode
    ejemplo:

    http://localhost:8000/ubication/countries/?search="mordor"
    sin las comillas

    retrieve:
    Retorna un país con id específico
    """
    queryset = Country.objects.all().order_by(Lower('name'))
    permission_classes = [DeveloperOnly]
    serializer_class = CountrySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'postalcode']

    def retrieve(self, request, pk):
        country = get_object_or_404(Country, pk=pk)
        serializer = CountrySerializer(country)
        return Response(serializer.data)

    def destroy(self, request, pk, ):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ProvinceViewSet(viewsets.ModelViewSet):
    """
    list:
    Filtra por name

    retrieve:
    Retorna una región con id específico
    """
    queryset = Province.objects.all()
    permission_classes = [DeveloperOnly]
    serializer_class = ProvinceSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def list(self, request, country_pk):
        provinces = Province.objects.filter(country=country_pk
                                        ).order_by(Lower('name'))
        serializer = self.get_serializer(provinces, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, country_pk):
        province = get_object_or_404(Province,
                                   Q(pk=pk) &
                                   Q(country=country_pk))
        serializer = ProvinceSerializer(province)
        return Response(serializer.data)

    def destroy(self, request, pk, country_pk):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CityViewSet(viewsets.ModelViewSet):
    """
    list:
    Filtra por name

    retrieve:
    Retorna una ciudad con id específico
    """
    queryset = City.objects.all()
    permission_classes = [DeveloperOnly]
    serializer_class = CitySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def list(self, request, country_pk, province_pk):
        cities = City.objects.filter(
            Q(province__country__id=country_pk) &
            Q(province=province_pk),
            ).order_by(Lower('name'))
        query = self.request.GET.get('search')
        if query:
            cities = cities.filter(
                Q(name__icontains=query))
        serializer = self.get_serializer(cities, many=True)
        return Response(serializer.data)

    def retrieve(self, request, country_pk, province_pk, pk):
        city = get_object_or_404(City,
                                 Q(province__country=country_pk) &
                                 Q(province=province_pk) &
                                 Q(pk=pk))
        serializer = CitySerializer(city)
        return Response(serializer.data)

    def destroy(self, request, pk, country_pk, province_pk):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
