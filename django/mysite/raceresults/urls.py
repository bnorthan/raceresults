from django.urls import path
from django.conf.urls import url
from . import views
from .views import AboutView

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', AboutView.as_view(), name='about.html'),
    path('runners/', views.runners, name='runners'),
    path('strava/', views.strava, name='strava'),
    url(r'^race/(?P<race_id>[0-9]+)/$', views.race, name='race'),
    url(r'^gp/(?P<race_id>[0-9]+)/$', views.gp, name='gp'),
    url(r'^runner/(?P<runner_id>[0-9]+)/$', views.runner, name='runner'),
    url(r'^search/$', views.search, name='search'),
]

