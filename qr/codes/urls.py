from django.conf.urls import url
from codes import views

urlpatterns = [
    url(r'^getcode/(?P<code>[\w\-]+)/$', views.GetCode.as_view()),
]
