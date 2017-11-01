from django.shortcuts import render
from items.models import Item


def index(request):
    items = Item.objects.all()
    return render(request, 'index.html', {'items': items})
