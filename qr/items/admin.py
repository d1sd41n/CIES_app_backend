from django.contrib import admin
from items.models import (Brand,
                          TypeItem,
                          Item,
                          LostItem,
                          Checkin,
                          )


admin.site.register(Brand)
admin.site.register(TypeItem)
admin.site.register(Item)
admin.site.register(LostItem)
admin.site.register(Checkin)
