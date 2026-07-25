from django.urls import path
from . import views
from . import location

app_name = 'core'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('landing/', views.landing, name='landing'),
    path('detect-location/', location.detect_location, name='detect_location'),
    path('seed-alerts/', views.seed_alerts, name='seed_alerts'),
    path('clear-weather-cache/', views.clear_weather_cache, name='clear_weather_cache'),
]
