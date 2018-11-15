from django.conf.urls import include, url
from rest_framework_nested import routers

from . import views

urlpatterns = [
    url(r'^email/$',
        views.EmailLostItem.as_view(), name='lost_item')
]
