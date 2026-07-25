from django.urls import path
from . import views
from . import simulator

app_name = 'telecom'
urlpatterns = [
    path('', simulator.simulator, name='simulator'),
    path('test/ussd/', simulator.test_ussd, name='test_ussd'),
    path('test/sms/', simulator.test_sms, name='test_sms'),
    path('ussd/', views.ussd_callback, name='ussd_callback'),
    path('sms/', views.sms_callback, name='sms_callback'),
    path('sms/send/', views.sms_send, name='sms_send'),
]
