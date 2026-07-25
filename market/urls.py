from django.urls import path
from . import views
app_name = 'market'
urlpatterns = [
    path('', views.price_list, name='prices'),
    path('markets/', views.market_list, name='markets'),
]
