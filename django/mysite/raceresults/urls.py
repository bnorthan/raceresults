from django.urls import path, re_path
from . import views
from .views import AboutView

urlpatterns = [
    path('', views.index, name='index'),
    path('races/<str:race_name>/', views.races, name='races'),
    path('about/', AboutView.as_view(), name='about.html'),
    path('runners/', views.runners, name='runners'),
    path('strava/', views.strava, name='strava'),
    path('stockade/most-races/', views.most_races, name='most_races'),
    path('stockade/active-streaks/', views.active_streaks, name='active_streaks'),
    path('stockade/longest-streaks/', views.longest_streaks, name='longest_streaks'),
    path('stockade/records/', views.records, name='stockade_records'),
    path('race/<int:race_id>/', views.race_by_id, name='race_by_id'),  # old id links
    path('race/<slug:race_slug>/', views.race, name='race'),
    re_path(r'^gp/(?P<race_id>[0-9]+)/$', views.gp, name='gp'),
    re_path(r'^runner/(?P<runner_id>[0-9]+)/$', views.runner, name='runner'),
    re_path(r'^search/$', views.search, name='search'),
    #url(r'^strava/$', views.search, name='search'),
]

