import qrcode
from io import BytesIO
from django.shortcuts import render
from items.models import Item
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4


def index(request):
    items = Item.objects.all()
    return render(request, 'index.html', {'items': items})


def generate_qr(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="somefilename.pdf"'

    buffer = BytesIO()

    p = canvas.Canvas(buffer, pagesize=A4)

    img = qrcode.make('1')
    img.save('img.png')
    for j in range(13):
        for i in range(18):
            p.drawInlineImage(img, j*45, i*45, width=50, height=50)

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
