from io import BytesIO

from django.core.files import File
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from codes.models import Code
from codes.serializers import CodesSerializer, GenerateCodesSerializer
from core.models import CustomUser, Seat
from items.models import Item
from qr.permissions import SupervisorAndSuperiorsOnly

import qrcode

class CompanyCodes(viewsets.ReadOnlyModelViewSet):
    """"
    Aqui se muestran todos los codes de una compañia,
    los usados y los no usados,

    Este endpoints es de solo lectura, para generar codes, se debe hacer
    desde los codes de la sede.

    Se filtra por id de la sede"""
    queryset = Code.objects.all()
    serializer_class = CodesSerializer

    filter_backends = [SearchFilter]
    search_fields = ['seat']

    def list(self, request, company_pk):
        queryset_list = Code.objects.filter(
            enabled=True,
            seat__company=company_pk,
        )
        query = self.request.GET.get("search")
        if query:
            if query.isdigit():
                queryset_list = queryset_list.filter(
                    Q(seat=query)
                ).distinct()
            else:
                return Response({"error": "solo ids"},
                                status=status.HTTP_400_BAD_REQUEST)
        serializer = CodesSerializer(queryset_list, many=True)
        return Response(serializer.data)


class GenerateCodes(APIView):
    """
    En este endpoint se generan páginas de códigos QR,
    como parámetro se ingresa la cantidad de páginas a generar
    {
    "pages": 1
    }"""
    serializer_class = GenerateCodesSerializer
    permission_classes = [GuardAndSuperiorsOnly]
    # lo siguiente pone un limite a la generacion de codigos al dia por usuario
    throttle_scope = 'generatecodes'

    def get(self, request, company_pk, seat_pk):
        return Response("El método GET no está soportado", status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, company_pk, seat_pk):
        serializer = GenerateCodesSerializer(data=request.data)
        if serializer.is_valid():
            seat = get_object_or_404(
                Seat,
                Q(id=seat_pk) &
                Q(company=company_pk)
            )
            pages = serializer.data['pages']
            if pages > 4:
                return Response("El máximo de páginas a crear a la vez es de 4 páginas", status=status.HTTP_400_BAD_REQUEST)
            elif pages < 0:
                return Response("No se crearon páginas nuevas", status=status.HTTP_400_BAD_REQUEST)
            seat = Seat.objects.get(pk=seat_pk)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="codigos.pdf"'
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            code_list = []
            for page in range(pages):
                for cols in range(13):
                    for rows in range(18):
                        code = Code()
                        code.seat = seat
                        code_list.append(code)
                        img = qrcode.make(str(code.code))
                        img.save('img.png')
                        p.drawInlineImage(img,
                                          cols * 45,
                                          rows * 45,
                                          width=50,
                                          height=50)
                p.showPage()
            Code.objects.bulk_create(code_list)
            p.save()
            pdf = buffer.getvalue()
            buffer.close()
            response.write(pdf)
            return response
