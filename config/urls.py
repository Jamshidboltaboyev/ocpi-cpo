from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .schema import swagger_urlpatterns

# from django_restful_admin import admin as api_admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/account/', include('apps.accounts.urls', namespace='accounts')),
    path('api/v1/core/', include('apps.core.urls', namespace='core')),
    # path('api/v1/payments/', include('uicpayment.urls')),

    # path('apiadmin/', api_admin.site.urls),
    # path('.well-known/apple-app-site-association', apple_app_site_association)
]

urlpatterns += swagger_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
