import qrcode
from io import BytesIO
from items.models import Item
from codes.models import Code
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib.pagesizes import A4


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
