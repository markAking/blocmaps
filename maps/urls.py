from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^building_detail/', views.building_detail, name='building_detail')
]