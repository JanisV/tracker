from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new/$', views.new, name='new'),
    url(r'^table/$', views.CompletionTableJson.as_view(), name='completeon_table_json'),
]
