from django.urls import path, re_path
from declaracion.views import (DeudasView,
                               DeudasDeleteView,PrestamoComodatoView, PrestamoComodatoDeleteView)

urlpatterns = [
    re_path(r'^deudas/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
            DeudasView.as_view(),
            name='deudas'),
    re_path(r'^deudas/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/agregar/$',
            DeudasView.as_view(), {'agregar': True},
            name='deudas-agregar'),
    re_path(r'^deudas/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/editar/(?P<pk>\d+)/$',
            DeudasView.as_view(),
            name='deudas-editar'),
    re_path(r'^deudas/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/borrar/(?P<pk>\d+)/$',
            DeudasDeleteView.as_view(),
            name='deudas-borrar'),

    re_path(r'^prestamoComodato/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
            PrestamoComodatoView.as_view(),
            name='prestamoComodato'),
    re_path(r'^prestamoComodato/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/agregar/$',
            PrestamoComodatoView.as_view(), {'agregar': True},
            name='prestamoComodato-agregar'),
    re_path(r'^prestamoComodato/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/editar/(?P<pk>\d+)/$',
            PrestamoComodatoView.as_view(),
            name='prestamoComodato-editar'),
    re_path(r'^prestamoComodato/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/borrar/(?P<pk>\d+)/$',
            PrestamoComodatoDeleteView.as_view(),
            name='prestamoComodato-borrar')
]
