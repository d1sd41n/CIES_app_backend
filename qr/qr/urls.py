from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^codes/', include('codes.urls')),
    url(r'^ubication/', include('ubication.urls')),
    url(r'^core/', include('core.urls')),
    url(r'^items/', include('items.urls')),

]
