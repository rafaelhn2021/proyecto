from django.urls import path
from django.conf.urls import url

from declaracion.views import (BusquedaDeclarantesFormView, InfoDeclarantesFormView, InfoDeclaracionFormView,
                               BusquedaDeclaracionesFormView, BusquedaUsuariosFormView, NuevoUsuariosOICFormView,
                               EliminarUsuarioFormView,InfoUsuarioFormView,EditarUsuarioFormView,DescargarReportesView,
                               DeclaracionesGraficas,DeclaracionesGraficasData,RegistroDeclaranteFormView)
from declaracion.views.admin import BusquedaUsDecFormView

urlpatterns = [
    path('busqueda-declarantes', BusquedaDeclarantesFormView.as_view(),
         name='busqueda-declarantes'),
    path('busqueda-declaraciones', BusquedaDeclaracionesFormView.as_view(),
         name='busqueda-declaraciones'),
    path('busqueda-usuarios', BusquedaUsuariosFormView.as_view(),
         name='busqueda-usuarios'),
         
    path('info-declarante/<int:pk>/<tipo_registro>/', InfoDeclarantesFormView.as_view(),
         name='info-declarante'),
    path('info-usuario/<int:pk>/', InfoUsuarioFormView.as_view(),
         name='info-usuario'),

    path('reporte/<tipo>', DescargarReportesView.as_view(),
         name='reporte'),

    path('declaraciones-graficas', DeclaracionesGraficas.as_view(),
         name='declaraciones-graficas'),

    path('api-graficas-data', DeclaracionesGraficasData.as_view(),
        name='api-graficas-data'), 

    path('eliminar-usuario/<int:pk>/', EliminarUsuarioFormView.as_view(),
         name='eliminar-usuario'),
    path('editar-usuario/<int:pk>/', EditarUsuarioFormView.as_view(),
         name='editar-usuario'),
    path('nuevo-usuario', NuevoUsuariosOICFormView.as_view(),
         name='nuevo-usuario'),

    path('nuevo-usuario-declarante',RegistroDeclaranteFormView.as_view(),
         name='nuevo-usuario-declarante'),
    path('editar-usuario-declarante/<int:pk>/<tipo_registro>/',RegistroDeclaranteFormView.as_view(),
         name='editar-usuario-declarante'),

    path('info-declaracion/<int:pk>/<tipo>/', InfoDeclaracionFormView.as_view(),
         name='info-declaracion'),
]
