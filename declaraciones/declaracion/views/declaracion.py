import uuid
import json
from django.views.generic import TemplateView
from django.views.generic.edit import DeleteView
from django.http import Http404, JsonResponse
from declaracion.models import Declaraciones,InfoPersonalFija
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from declaracion.models import SeccionDeclaracion

from .utils import guardar_estatus

from sitio.models import sitio_personalizacion

class DeclaracionView(TemplateView):
    """
    Class DeclaracionView obtiene información de la declaración actual en relación al usuario logeado
    """
    template_name = "declaracion/index.html"
    @method_decorator(login_required(login_url='/login'))
    def get(self,request,*args,**kwargs):
        tipos_declaracion_usuario = [0,0,0]
        agregar_nueva_inicial = True

        try:
            declaracion_modificacion_crear = sitio_personalizacion.objects.first().declaracion_modificacion_crear
        except:
            declaracion_modificacion_crear = True

        try:
            usuario = InfoPersonalFija.objects.filter(usuario=request.user).first()
            declaraciones_usuario = Declaraciones.objects.filter(info_personal_fija=usuario)

            declaracion_en_curso = declaraciones_usuario.filter(
                Q(cat_estatus__isnull=True) | Q(cat_estatus__pk__in=(1, 2, 3))).first()

            for declaracion in declaraciones_usuario.filter(Q(cat_estatus__pk=4)):
                if declaracion.cat_tipos_declaracion.pk == 1:
                    tipos_declaracion_usuario[0] = tipos_declaracion_usuario[0] + 1
                if declaracion.cat_tipos_declaracion.pk == 2:
                    tipos_declaracion_usuario[1] = tipos_declaracion_usuario[1] + 1
                if declaracion.cat_tipos_declaracion.pk == 3:
                    tipos_declaracion_usuario[2] = tipos_declaracion_usuario[2] + 1

            if tipos_declaracion_usuario[0] > 0 and tipos_declaracion_usuario[2] == 0:
                agregar_nueva_inicial = False


        except:
            declaracion = None
        
        return render(request,self.template_name,{'declaracion_en_curso':declaracion_en_curso, 'declaracion_modificacion_crear': declaracion_modificacion_crear,'agregar_nueva_inicial': agregar_nueva_inicial})


class DeclaracionDeleteView(DeleteView):
    """
    Class DeclaracionDeleteView vista basada en clases muestra página de confirmación y eimina un objeto existente
    ------------
    El objeto dado solo se eliminará si el metodo de solicitud es POST
    """
    def get(self, request, *args,**kwargs):
        raise Http404("")
        
    def get_object(self, queryset=None):
        try:
            folio_declaracion = self.kwargs['folio']
            pk = self.kwargs['pk']
            declaracion_obj = Declaraciones.objects.filter(
                folio=uuid.UUID(folio_declaracion),
                info_personal_fija__usuario=self.request.user
                ).first()
            registros = self.model.objects.filter(
                pk=pk,
                declaraciones=declaracion_obj
                ).first()

            if "seccion" in locals():
                if self.seccion == "prestamocomodato":
                    tipo_comodato = registros.tipo_obj_comodato

                    campo_default_existente_m = self.model.objects.filter(declaraciones=declaracion_obj,campo_default=True,cat_tipos_muebles__isnull=False)
                    campo_default_existente_in = self.model.objects.filter(declaraciones=declaracion_obj,campo_default=True,cat_tipos_inmueble__isnull=False)
                     
                    if tipo_comodato == "INMUEBLE":

                        if len(campo_default_existente_m) > 0:
                            campo_default_existente_m.first().delete()
                        else:
                            comodato_default_inmueble = self.model(
                                cat_tipos_inmueble = self.cat_tipos_inmueble.objects.get(pk=9),
                                campo_default = True,
                                declaraciones= declaracion_obj
                            )
                            comodato_default_inmueble.save()
                            

                    if tipo_comodato == "MUEBLE":
                        if len(campo_default_existente_in) > 0:
                            campo_default_existente_in.first().delete()
                        else:
                            comodato_default_mueble = self.model(
                                cat_tipos_muebles = self.cat_tipos_muebles.objects.get(pk=9),
                                campo_default = True,
                                declaraciones= declaracion_obj        
                            )
                            comodato_default_mueble.save()

        except Exception as e:
            print (e)
            raise Http404("")
        return registros

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return JsonResponse({'delete': 'ok'})
