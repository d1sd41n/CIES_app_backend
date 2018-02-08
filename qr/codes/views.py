from rest_framework.response import Response
from codes.serializers import CodesSerializer
from codes.models import Code
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import qrcode
from io import BytesIO
from items.models import Item
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib.pagesizes import A4
from rest_framework import viewsets


def index(request):
    items = Item.objects.all()
    return render(request, 'index.html', {'items': items})


def generate_qr(request):
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


class GetCode(APIView):
    """muestra un codigo, se debe ingresar la url de la siguiente manera:
    http://localhost:8000/codes/getcode/ff0d0ddb-c055-4824-9844-104e4c94f01d/

    lo que sigue despues de /getcode/ es el hash que se desa buscar"""
    def get(self, request, code, format=None):
        code = get_object_or_404(
               Code,
               code=code,
               )
        serializer = CodesSerializer(code)
        return Response(serializer.data)


# class CodesViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     This viewset automatically provides `list` and `detail` actions.
#     """
#     print("dfdfgfggfggfdgfergefe")


class CodesView(APIView):

    def get(self, request, format=None):
        print("CodeView")
        code = Code.objects.all()
        serializer = CodesSerializer(code, many=True)
        return Response(serializer.data)
