from django.contrib import admin
from core.models import (CustomUser,
                         Company,
                         Seat,
                         Visitor,
                         )

admin.site.register(CustomUser)
admin.site.register(Company)
admin.site.register(Seat)
admin.site.register(Visitor)
