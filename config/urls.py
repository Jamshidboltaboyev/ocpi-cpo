from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.versions.views import VersionListAPIView, VersionV2_2_1_DetailAPIView
from .schema import swagger_urlpatterns

# from django_restful_admin import admin as api_admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ocpi/versions/', VersionListAPIView.as_view()),
    path('ocpi/2.2.1/details', VersionV2_2_1_DetailAPIView.as_view()),



    path("cpo/2.2.1/locations/", include('apps.locations.urls')),
    path("cpo/2.2.1/credentials/", include('apps.credentials.urls'))
]

urlpatterns += swagger_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
