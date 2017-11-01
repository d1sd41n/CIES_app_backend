from django.contrib import admin
from items.models import (Brand,
                          TypeItem,
                          Item)


admin.site.register(Brand)
admin.site.register(TypeItem)
admin.site.register(Item)
