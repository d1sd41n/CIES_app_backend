from django.conf.urls import url
from codes import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'Cooodes', views.CodesViewSet)   CodesView

urlpatterns = [
    url(r'^getcode/(?P<code>[\w\-]+)/$', views.GetCode.as_view()),
    url(r'^r/', views.CodesView.as_view()),
    # url(r'^', include(router.urls)),
]
