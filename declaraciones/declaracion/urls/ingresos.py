from django.urls import path, re_path
from declaracion.views import IngresosDeclaracionView
from django.views.generic import TemplateView

urlpatterns = [

     re_path(r'^ingresos-netos/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
            IngresosDeclaracionView.as_view(),
            name='ingresos-netos'),

     re_path(r'^ingresos-servidor-publico/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
            IngresosDeclaracionView.as_view(),
            name='ingresos-servidor-publico')
]