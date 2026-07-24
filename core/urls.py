from django.urls import path
from . import views
from . import location

app_name = 'core'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('landing/', views.landing, name='landing'),
    path('detect-location/', location.detect_location, name='detect_location'),
]
