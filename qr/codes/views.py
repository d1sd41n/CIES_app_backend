from rest_framework.response import Response
from codes.serializers import CodesSerializer
from codes.models import Code
import qrcode
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import status
from io import BytesIO
from items.models import Item
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib.pagesizes import A4
from rest_framework import viewsets
from django.db.models import Q
from rest_framework.filters import (
    SearchFilter,
)


class CompanyCodes(viewsets.ReadOnlyModelViewSet):
    """"
    Aqui se muestran todos los codes de una compañia,
    los usados y los no usados,

    Este endpoints es de solo lectura, para generar codes, se debe hacer
    desde los codes de la sede.

    Se filtra por id de la sede"""
    permission_classes = (DRYPermissions,)
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


def index(request):
    items = Item.objects.all()
    return render(request, 'index.html', {'items': items})


def generate_qr(request, company_pk, seat_pk):
    if request.method == 'GET':
        return render(request, 'form_pdf.html')
    elif request.method == 'POST':
        pages = int(request.POST['pages'])
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="somefilename.pdf"'
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        for page in range(pages):
            for cols in range(13):
                for rows in range(18):
                    code = Code()
                    code.save()
                    # // probablemente tenga que borrar estas 3 lineas
                    img = qrcode.make(str(code.code))
                    img.save('img.png')
                    p.drawInlineImage(img,
                                      cols*45,
                                      rows*45,
                                      width=50,
                                      height=50)
            p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
