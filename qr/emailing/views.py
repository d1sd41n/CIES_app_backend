from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from items.models import Item
from time import gmtime, strftime
import datetime
from django.db.models import Q
from core.models import CustomUser, Seat
from rest_framework import status
from qr.permissions import GuardAndSuperiorsOnly

class EmailLostItem(APIView):
    """
    Se debe introducir el id del objeto perdido
    <pre>
    {
    "id":1
    }
    </pre>
    """
    permission_classes = [GuardAndSuperiorsOnly]

    def post(self, request, company_pk, seat_pk, format=None):
        dias = ["Lunes", "Martes", "Miercoles", "Jueves",
                "Viernes", "Sabado", "Domingo"]
        id_item = request.data["id"]
        item = Item.objects.get(id=id_item)
        type_item = item.type_item.kind
        brand_item = item.brand.brand
        first_name = item.owner.first_name
        last_name = item.owner.last_name
        id_visitor = item.owner.last_name
        vivitor_email = item.owner.email
        date = str(datetime.datetime.today().strftime('%d-%m-%Y %H:%M"'))
        day_date = dias[datetime.datetime.today().weekday()]
        company_nit = item.seat_registration.company.nit
        company_name = item.seat_registration.company.name
        company_website = item.seat_registration.company.website
        seat = CustomUser.objects.get(user=request.user).seat.name
        seat_phone = CustomUser.objects.get(user=request.user).seat.phone
        seat_email = CustomUser.objects.get(user=request.user).seat.email
        guard_name = request.user.first_name
        guard_last_name = request.user.last_name

        Asunto = "Hemos encontrado su "+str(type_item)
        Mensaje = "Estimado {} {}, \
Este correo es para informarle que el día {} del {} se ha localizado su {} en \
la sede: {} como objeto olvidado. \
Podrá recoger su pertenencia en la respectiva sede donde se encontró, en el horario de \
____________  y será indispensable que lleve consigo su documento de identidad para proceder \
a entregar su pertenencia, de lo contrario, no se podrá devolverle el objeto.\n \
Muchas gracias.\n \
Atentamente: {} {}\n \
{}\n \
{}, {} | {}\n \
{} \ ".format(first_name,last_name, day_date, date, type_item, seat, guard_name, guard_last_name,
              company_name, seat, seat_email, seat_phone, company_website)
        send_mail(Asunto, Mensaje, 'example@example.com', [vivitor_email], fail_silently=False)
        return Response({"Email":"enviado"})
