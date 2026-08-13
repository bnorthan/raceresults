from django.urls import path, re_path
from . import views
from .views import AboutView

urlpatterns = [
    path('', views.index, name='index'),
    path('races/<str:race_name>/', views.races, name='races'),
    path('about/', AboutView.as_view(), name='about.html'),
    path('runners/', views.runners, name='runners'),
    path('strava/', views.strava, name='strava'),
    re_path(r'^race/(?P<race_id>[0-9]+)/$', views.race, name='race'),
    re_path(r'^gp/(?P<race_id>[0-9]+)/$', views.gp, name='gp'),
    re_path(r'^runner/(?P<runner_id>[0-9]+)/$', views.runner, name='runner'),
    re_path(r'^search/$', views.search, name='search'),
    #url(r'^strava/$', views.search, name='search'),
]

