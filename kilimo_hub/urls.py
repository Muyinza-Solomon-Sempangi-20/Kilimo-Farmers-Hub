from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('core.urls')),
    path('crops/', include('crops.urls')),
    path('market/', include('market.urls')),
    path('disease/', include('disease.urls')),
    path('veterinary/', include('veterinary.urls')),
    path('weather/', include('weather.urls')),
    path('i18n/', include('translation.urls')),
    path('telecom/', include('telecom.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
