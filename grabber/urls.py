from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new/$', views.new, name='new'),
    url(r'^table/$', views.CompletionTableJson.as_view(), name='completeon_table_json'),
    url(r'^run/$', views.run, name='run'),
    url(r'^raw/$', views.raw, name='raw_table'),
    url(r'^raw_json/$', views.RawTableJson.as_view(), name='raw_table_json'),
]

urlpatterns += static('images/', document_root=settings.MEDIA_ROOT)
