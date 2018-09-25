from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.authtoken import views
from rest_framework.permissions import AllowAny

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="IDRA API",
        default_version='v1',
        description="Made by Evol",
        terms_of_service="https://gitlab.com/hydrasoft2017/qr-backend",
        contact=openapi.Contact(email="evolpoint@gmail.com"),
        license=openapi.License(name="IDK License"),
    ),
    validators=['ssv'],
    public=True,
    permission_classes=(AllowAny,),
)


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^codes/', include('codes.urls')),
    url(r'^ubication/', include('ubication.urls')),
    url(r'^core/', include('core.urls')),
    url(r'^items/', include('items.urls')),
    url(r'^disabled/', include('disabled.urls')),
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger',
                                           cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc',
                                         cache_timeout=0), name='schema-redoc'),
    url(r'^api-token-auth/', views.obtain_auth_token)
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
