from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions
from django.core.mail import send_mail
from items.models import Item
from time import gmtime, strftime
from django.db.models import Q
from core.models import CustomUser, Seat
from rest_framework import status


class EmailLostItem(APIView):
    """
    Se debe introducir el id del objeto perdido
    <pre>
    {
    "id":1
    }
    </pre>
    """

    def permissions(self, request):
        """
        Ya que es sólo una vista la que necesita estos
        permisos se harán de esta manera y no usando los de DRF."""

        developer_permission = request.user.groups.filter(
            Q(name="Developer"))

        if developer_permission:
            return 1
        group = request.user.groups.filter(Q(name="manager") |
                                           Q(name="Security Boss"))
        print(len(group)==1)
        parameters = [parameter for parameter in request.path_info
                      if parameter.isdigit()]
        user_company = str(CustomUser.objects.get(
            user=request.user).seat.company.id)
        user_seat = str(CustomUser.objects.get(user=request.user).seat.id)
        if (len(group)==1 and user_company == parameters[0]
                and user_seat == parameters[1]):
                return 1
        return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, request, company_pk, seat_pk, format=None):
        permission = self.permissions(request)
        if permission != 1:
            return permission
        id_item = request.data["id"]
        item = Item.objects.get(id=id_item)
        type_item = item.type_item.kind
        brand_item = item.brand.brand
        first_name = item.owner.first_name
        last_name = item.owner.last_name
        id_visitor = item.owner.last_name
        vivitor_email = item.owner.email
        date = strftime("%Y-%m-%d %H:%M", gmtime())
        company_nit = item.seat_registration.company.nit
        company_name = item.seat_registration.company.name
        company_website = item.seat_registration.company.website

        Asunto = "Hemos encontrado su "+str(type_item)
        Mensaje = "Estimado {} {}, \
Este correo es para informarle que el día __ del {} se ha localizado su {} en \
#aqui va la sede donde se encontro# como objeto olvidado. \
Podrá recoger su pertenencia en la respectiva sede donde se encontró, en el horario de \
____________  y será indispensable que lleve consigo su documento de identidad para proceder \
a entregar su pertenencia, de lo contrario, no se podrá devolverle el objeto.\n \
Muchas gracias.\n \
Atentamente: #Aqui va ir el nombre del empleado que envia el correo#\n \
{}\n \
#Aqui va la sede de desde donde se envio #,#Aqui va el correo de la sede desde donde envio###,|#Aqui va ir el telefono de la sede de donde se envia el correo#\n \
{} \ ".format(first_name,last_name, date, type_item, company_name,company_website)
        send_mail(Asunto, Mensaje, 'example@example.com', [vivitor_email], fail_silently=False)
        return Response({"Email":"enviado"})
