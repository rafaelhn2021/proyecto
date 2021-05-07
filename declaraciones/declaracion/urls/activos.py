from django.urls import path, re_path
from django.conf.urls import url

from declaracion.views import (BienesMueblesView, BienesInmueblesView,
                               MueblesNoRegistrablesView, InversionesView,
                               FideicomisosView,
                               BienesInmueblesDeleteView, BienesMueblesDeleteView,
                               MueblesNoRegistrablesDeleteView,
                               InversionesDeleteView,
                               FideicomisosDeleteView,listaTiposInversionesEspecificos)

urlpatterns = [
    re_path(
        r'^bienes-inmuebles/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
        BienesInmueblesView.as_view(), name='bienes-inmuebles'),
    re_path(
        r'^bienes-inmuebles/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/agregar/$',
        BienesInmueblesView.as_view(), {'agregar': True}, name='bienes-inmuebles-agregar'),
    re_path(
        r'^bienes-inmuebles/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/editar/(?P<pk>\d+)/$',
        BienesInmueblesView.as_view(), name='bienes-inmuebles-editar'),
    re_path(
        r'^bienes-inmuebles/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/borrar/(?P<pk>\d+)/$',
        BienesInmueblesDeleteView.as_view(), name='bienes-inmuebles-borrar'),

    re_path(
        r'^bienes-muebles/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
        BienesMueblesView.as_view(), name='bienes-muebles'),
    re_path(
        r'^bienes-muebles/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/agregar/$',
        BienesMueblesView.as_view(), {'agregar': True}, name='bienes-muebles-agregar'),
    re_path(
        r'^bienes-muebles/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/editar/(?P<pk>\d+)/$',
        BienesMueblesView.as_view(), name='bienes-muebles-editar'),
    re_path(
        r'^bienes-muebles/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/borrar/(?P<pk>\d+)/$',
        BienesMueblesDeleteView.as_view(), name='bienes-muebles-borrar'),

    re_path(
        r'^muebles-noregistrables/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
        MueblesNoRegistrablesView.as_view(), name='muebles-noregistrables'),
    re_path(
        r'^muebles-noregistrables/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/agregar/$',
        MueblesNoRegistrablesView.as_view(), {'agregar': True}, name='muebles-noregistrables-agregar'),
    re_path(
        r'^muebles-noregistrables/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/editar/(?P<pk>\d+)/$',
        MueblesNoRegistrablesView.as_view(), name='muebles-noregistrables-editar'),
    re_path(
        r'^muebles-noregistrables/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/borrar/(?P<pk>\d+)/$',
        MueblesNoRegistrablesDeleteView.as_view(), name='muebles-noregistrables-borrar'),

    re_path(
        r'^inversiones/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
        InversionesView.as_view(), name='inversiones'),
    re_path(
        r'^inversiones/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/agregar/$',
        InversionesView.as_view(), {'agregar': True}, name='inversiones-agregar'),
    re_path(
        r'^inversiones/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/editar/(?P<pk>\d+)/$',
        InversionesView.as_view(), name='inversiones-editar'),
    re_path(
        r'^inversiones/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/borrar/(?P<pk>\d+)/$',
        InversionesDeleteView.as_view(), name='inversiones-borrar'),

    re_path(
        r'^fideicomisos/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
        FideicomisosView.as_view(), name='fideicomisos'),
    re_path(
        r'^fideicomisos/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/agregar/$',
        FideicomisosView.as_view(), {'agregar': True}, name='fideicomisos-agregar'),
    re_path(
        r'^fideicomisos/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/editar/(?P<pk>\d+)/$',
        FideicomisosView.as_view(), name='fideicomisos-editar'),
    re_path(
        r'^fideicomisos/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/borrar/(?P<pk>\d+)/$',
        FideicomisosDeleteView.as_view(), name='fideicomisos-borrar'),

    url(r'^ajax/lista_tiposinversionesespecificas/$', listaTiposInversionesEspecificos, name='lista_tiposinversionesespecificas'),
]
