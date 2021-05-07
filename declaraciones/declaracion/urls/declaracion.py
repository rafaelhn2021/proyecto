from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from declaracion.views import (DeclaracionView)

urlpatterns = [
    path('', DeclaracionView.as_view(), name="declaracion"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)