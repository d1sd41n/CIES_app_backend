from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.response import Response
from ubication.models import Country, Region, City

from ubication.serializers import (
    CountrySerializerList,
    CountrySerializerDetail,
    RegionSerializerDetail,
    RegionSerializerList,
    CitySerializerList,
    CitySerializerDetail,
)


class CountryViewSet(viewsets.ModelViewSet):
    """
    list:
    Filtra por name y postalcode
    ejemplo:

    http://localhost:8000/ubication/countries/?search="mordor"
    sin las comillas

    retrieve:
    Retorna un país con id específico
    """
    permission_classes = (DRYPermissions,)
    queryset = Country.objects.all().order_by(Lower('name'))
    serializer_class = CountrySerializerList
    filter_backends = [SearchFilter]
    search_fields = ['name', 'postalcode']

    def retrieve(self, request, pk):
        country = get_object_or_404(Country, pk=pk)
        serializer = CountrySerializerDetail(country)
        return Response(serializer.data)


class RegionViewSet(viewsets.ModelViewSet):
    """
    list:
    Filtra por name

    retrieve:
    Retorna una región con id específico
    """
    permission_classes = (DRYPermissions,)
    queryset = Region.objects.all()
    serializer_class = RegionSerializerList
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def list(self, request, country_pk):
        regions = Region.objects.filter(country=country_pk
                                        ).order_by(Lower('name'))
        query = self.request.GET.get('search')
        if query:
            regions = regions.filter(Q(name__icontains=query))
        serializer = self.get_serializer(regions, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, country_pk=None):
        region = get_object_or_404(Region,
                                   Q(pk=pk) &
                                   Q(country=country_pk))
        serializer = RegionSerializerDetail(region)
        return Response(serializer.data)


class CityViewSet(viewsets.ModelViewSet):
    """
    list:
    Filtra por name

    retrieve:
    Retorna una ciudad con id específico
    """
    permission_classes = (DRYPermissions,)
    queryset = City.objects.all()
    serializer_class = CitySerializerList
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def list(self, request, country_pk, region_pk):
        cities = City.objects.filter(
            Q(region__country=country_pk) &
            Q(region=region_pk)).order_by(Lower('name'))
        query = self.request.GET.get('search')
        if query:
            cities = cities.filter(
                Q(name__icontains=query))
        serializer = self.get_serializer(cities, many=True)
        return Response(serializer.data)

    def retrieve(self, request, country_pk, region_pk, pk):
        city = get_object_or_404(City,
                                 Q(region__country=country_pk) &
                                 Q(region=region_pk) &
                                 Q(pk=pk))
        serializer = CitySerializerDetail(city)
        return Response(serializer.data)
