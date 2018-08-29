from django.contrib import admin
from ubication.models import (Country,
                              Province,
                              City,
                              Location)

admin.site.register(Country)
admin.site.register(Province)
admin.site.register(City)
admin.site.register(Location)
