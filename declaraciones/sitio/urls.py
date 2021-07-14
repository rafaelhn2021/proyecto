from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, re_path, reverse_lazy
from django.contrib.auth import views as auth_views

from declaracion.views import PerfilView

from .views import (IndexView, LoginView, LogoutView, FAQView, DeclaracionesPreviasView, PasswordResetRFCView, 
                    DeclaracionesPreviasDescargarView, activar, CambioPasswordView, 
                    PersonalizacionCatalogoPuestosView,
                    PersonalizacionDatosEntidadView,
                    PersonalizacionCatalogoAreasView,
                    DeclaracionesPreviasVerView,
                    GenerarHTMLView,
                    consultaEstatusTaskPDFDeclaracion, crearPDFDeclaracion, eliminarProcesoPDF, PdfConfirmacion)

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('inicio', PerfilView.as_view(), name="inicio"),
    path('preguntas-frecuentes', FAQView.as_view(), name="preguntas-frecuentes"),
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('declaraciones-previas', DeclaracionesPreviasView.as_view(), name="declaraciones-previas"),
    re_path(r'^declaraciones-previas/descargar/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
            DeclaracionesPreviasDescargarView.as_view(),
            name="declaraciones-previas-descargar"),
    re_path(r'^declaraciones-previas/ver/(?P<folio>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/$',
            DeclaracionesPreviasVerView.as_view(),
            name="declaraciones-previas-ver"),
    url(r'^activar/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activar, name='activar'),
    path('cambiar', CambioPasswordView.as_view(), name="cambiar"),
    path('recuperar', LogoutView.as_view(), name="recuperar"),
    path('password_reset/', PasswordResetRFCView.as_view(success_url=reverse_lazy('password_reset_done')),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('personalizar/catalogos/puestos', PersonalizacionCatalogoPuestosView.as_view(), name='personalizar_catpuestos'),
    path('personalizar/catalogos/puestos/agregar', PersonalizacionCatalogoPuestosView.as_view(), name='personalizar_catpuestos_agregar'),
    path('personalizar/catalogos/puestos/editar-<slug:pkid>', PersonalizacionCatalogoPuestosView.as_view(), name='personalizar_catpuestos_editar'),
    path('personalizar/catalogos/puestos/eliminar-<int:pkid>', PersonalizacionCatalogoPuestosView.as_view(), name='personalizar_catpuestos_eliminar'),

    path('personalizar/catalogos/areas', PersonalizacionCatalogoAreasView.as_view(), name='personalizar_catareas'),
    path('personalizar/catalogos/areas/agregar', PersonalizacionCatalogoAreasView.as_view(), name='personalizar_catareas_agregar'),
    path('personalizar/catalogos/areas/editar-<slug:pkid>', PersonalizacionCatalogoAreasView.as_view(), name='personalizar_catareas_editar'),
    path('personalizar/catalogos/areas/eliminar-<int:pkid>', PersonalizacionCatalogoAreasView.as_view(), name='personalizar_catareas_eliminar'),

    path('personalizar/datos_entidad', PersonalizacionDatosEntidadView.as_view(), name='personalizar_entidad'),
    path('personalizar/datos_entidad/editar', PersonalizacionDatosEntidadView.as_view(), name='personalizar_entidad_editar'),
   
    path('generar_html', GenerarHTMLView, name='generar_html'),
    url(r'^declaraciones-previas/estatus_pdf_declaracion/$', consultaEstatusTaskPDFDeclaracion, name='estatus_pdf_declaracion'),
    url(r'^declaraciones-previas/crear_pdf_declaracion/$', crearPDFDeclaracion, name='crear_pdf_declaracion'),
    url(r'^declaraciones-previas/eliminar_pdf_declaracion/$', eliminarProcesoPDF, name='eliminar_pdf_declaracion'),
	path('pdf_confimacion/<int:pk>/', PdfConfirmacion.as_view(), name="pdf_confimacion"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)