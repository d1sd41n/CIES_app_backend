from django.conf.urls import url, include
from django.contrib import admin
from codes.views import generate_qr
from django.conf import settings
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Pastebin API')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^pdf/', generate_qr),
    url(r'^codes/', include('codes.urls')),
    url(r'^ubication/', include('ubication.urls')),
    url(r'^core/', include('core.urls')),
    url(r'^items/', include('items.urls')),
    url(r'^docs/', schema_view),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
    url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
