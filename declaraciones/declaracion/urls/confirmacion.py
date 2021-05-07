from django.urls import re_path

from declaracion.views import (ConfirmarDeclaracionView, ConfirmacionAllinOne)

urlpatterns = [
    re_path(r'^confirmar-declaracion/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
         ConfirmarDeclaracionView.as_view(), name="confirmar-declaracion"),
    re_path(r'^confirmar/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
         ConfirmacionAllinOne.as_view(), name="confirmar-allinone"),
]
