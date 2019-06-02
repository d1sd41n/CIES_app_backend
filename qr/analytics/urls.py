from django.conf.urls import include, url

from analytics import views


urlpatterns = [
    url(r'^companies/(?P<company_pk>\d+)/seats/(?P<seat_pk>\d+)/basics/$',
        views.BasicsAnalyticsView.as_view(), name='analytics'),
]
