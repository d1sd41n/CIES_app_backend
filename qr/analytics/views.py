from django.db.models import F, Q
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Company, CustomUser, Seat, Visitor
from items.models import Brand, CheckIn, Item, LostItem, TypeItem
from qr.permissions import (DeveloperOnly, ManagerAndSuperiorsOnly,
                            SupervisorAndSuperiorsOnly, GuardAndSuperiorsOnly)

import datetime




class BasicsAnalyticsView(APIView):
    """
    En este endpoint se lista un resumen de los datos basicos de la compañia:
    Numero del total de items:  "items_total",
    Numero de total items perdidos: lost_items_total,
    Numero total de items perdidos: "not_lost_items_total",
    El total de cada uno de los items de cada tipo,
    Numero total de visistantes registrados en la compañia: "visitors_total"

    """
    permission_classes = [GuardAndSuperiorsOnly]

    def get(self, request, company_pk, seat_pk):

        # Analytics items
        data = {} # dict for save the data

        type_item = TypeItem.objects.filter( # get type items
            enabled=True
        )
        items_total = 0
        for item in type_item:
            item_total = Item.objects.filter( #get the num items of each kind of item
                company__pk=company_pk,
                owner__company__pk=company_pk,
                type_item__pk=item.pk,
            ).count()
            data[item.kind] = item_total
            items_total += item_total

        lost_items_total = Item.objects.filter( # get lost items
            company__pk=company_pk,
            owner__company__pk=company_pk,
            lost=True,
        ).count()
        not_lost_items_total = items_total - lost_items_total

        data["items_total"] = items_total
        data["lost_items_total"] = lost_items_total
        data["not_lost_items_total"] = not_lost_items_total

        # Analytics Visitors
        visitors_total = Visitor.objects.filter(
            enabled=True,
            company__pk=company_pk
        ).count()

        data["visitors_total"] = visitors_total

        return Response(data, status=status.HTTP_200_OK)
