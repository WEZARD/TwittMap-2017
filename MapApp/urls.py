from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^handle/$', views.handle, name='handle'),
    url(r'^handle_sns/$', views.handle_sns, name='handle_sns'),
    url(r'^polling/$', views.polling, name='polling')
]