from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions
from django.core.mail import send_mail


class EmailLostItem(APIView):
    #permission_classes = (DRYPermissions,)

    def get(self, request, format=None):
        send_mail('sddfdsfdsfdsdfdsf', 'Here is thsssse message.', 'from@example.com', ['megajaah@gmail.com'], fail_silently=False)
        print("qqqq")
        return Response({"yes":1})
