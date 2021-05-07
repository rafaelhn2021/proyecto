from django.urls import path
from django.conf.urls import url

from declaracion.views import (RegistroView,PerfilView,listaPuestos)

urlpatterns = [

    path('nuevo', RegistroView.as_view(),
         name='nuevo'),
    path('perfil', PerfilView.as_view(),
         name='perfil'),
    url(r'^lista_puestos/$', listaPuestos, name="lista_puestos"),
]
