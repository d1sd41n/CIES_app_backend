from django.contrib import admin
from core.models import (CustomUser,
                         Company,
                         Seat)


admin.site.register(CustomUser)
admin.site.register(Company)
admin.site.register(Seat)
