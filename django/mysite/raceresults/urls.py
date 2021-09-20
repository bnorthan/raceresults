from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('runners/', views.runners, name='runners'),
    #path('race/<int:race_id>/', views.race, name='race'),
    url(r'^race/(?P<race_id>[0-9]+)/$', views.race, name='race'),
    url(r'^gp/(?P<race_id>[0-9]+)/$', views.gp, name='gp'),
    url(r'^runner/(?P<runner_id>[0-9]+)/$', views.runner, name='runner'),
    
]

