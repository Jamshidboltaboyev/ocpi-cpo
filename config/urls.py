from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .schema import swagger_urlpatterns

# from django_restful_admin import admin as api_admin


urlpatterns = [
    path('admin/', admin.site.urls),

    path("cpo/2.2.1/locations/", include('apps.locations.urls'))
]

urlpatterns += swagger_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
