from django.urls import path
from . import views

app_name = 'telecom'
urlpatterns = [
    path('ussd/', views.ussd_callback, name='ussd_callback'),
    path('sms/', views.sms_callback, name='sms_callback'),
    path('sms/send/', views.sms_send, name='sms_send'),
]
