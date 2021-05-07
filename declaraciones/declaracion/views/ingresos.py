import uuid
from django.conf import settings
from django.urls import reverse_lazy, resolve
from django.views import View
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from declaracion.forms import (ObservacionesForm, DomiciliosForm,
                               InfoPersonalVarForm,IngresosDeclaracionForm)
from declaracion.models import (Declaraciones, SeccionDeclaracion,
                                SeccionDeclaracion, Secciones,IngresosDeclaracion,ConyugeDependientes,InfoPersonalFija)

from .utils import (guardar_estatus, no_aplica, declaracion_datos,
                    validar_declaracion, obtiene_avance,campos_configuracion,actualizar_ingresos,
                    get_declaracion_anterior)
from .declaracion import (DeclaracionDeleteView)
from django.contrib import messages
import json

class IngresosDeclaracionView(View):
    """
    Class IngresosDeclaracionView vista basada en clases, carga y guardar ingresosDeclaración(Sección: VIII.INGRESOS NETOS DECLARANTE Y IX.TE DESEMPEÑASTE COMO SERVIDOR PÚBLICO?)
    Esta vista es usada en dos secciones que usan practicamento los mismos formularios a excepcion de algunos campos que los diferencian
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/ingresos/ingresos-declaracion.html'

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        """
        Una sección puede estar conformado por más de un modelo y un formulario
        Se inicializan algunos campos con valores predeterminados, frecuentemente serán moneda y entidad federativa
        """
        folio_declaracion = self.kwargs['folio']

        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        seccion = Secciones.objects.filter(url=current_url).first()

        tipo_ingreso = True
        ingresos_pareja = 0
        if current_url == 'ingresos-servidor-publico':
            tipo_ingreso = False

        avance, faltas = 0, None
        try:
            declaracion = validar_declaracion(request, folio_declaracion)
            avance, faltas = obtiene_avance(declaracion)
        except ObjectDoesNotExist as e:
            raise Http404()

        try: 
            ingresos_declaracion_data = IngresosDeclaracion.objects.filter(declaraciones=declaracion, tipo_ingreso=tipo_ingreso).first()        
        except:
            ingresos_declaracion_data = None
        
        # Busca información de una declaración previa si es de tipo MODIFICACIÓN/CONCLUSIÓN
        # Solo se obtiene información previa si la declaración actual aún no tiene registro de esta sección
        if declaracion.cat_tipos_declaracion.codigo != 'INICIAL':              
            if not ingresos_declaracion_data:
                declaracion_anterior = get_declaracion_anterior(declaracion)

                if declaracion_anterior:
                    ingresos_declaracion_data = declaracion_anterior.ingresosdeclaracion_set.filter(tipo_ingreso=tipo_ingreso).first()

                    if ingresos_declaracion_data:
                        ingresos_declaracion_data.pk = None
                        ingresos_declaracion_data.observaciones.pk = None

                        #Si la declaración ya tiene registros de la pareja o dependientes con un salario se toma ese dato
                        # y no el de la declaración anterior
                        if tipo_ingreso:
                            pareja_dependieintes = ConyugeDependientes.objects.filter(declaraciones=declaracion) 
                            if pareja_dependieintes:
                                ingresos_pareja = actualizar_ingresos(declaracion)
                                ingresos_declaracion_data.ingreso_mensual_pareja_dependientes = ingresos_pareja 




        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicpal
        if ingresos_declaracion_data:
            observaciones_data =  ingresos_declaracion_data.observaciones
            
            if ingresos_declaracion_data.ingreso_mensual_total is None or not ingresos_declaracion_data.ingreso_mensual_total:
                ingresos_declaracion_data.ingreso_mensual_total = 0
            ingresos_declaracion_data = model_to_dict(ingresos_declaracion_data)
            observaciones_data = model_to_dict(observaciones_data)
        else:

            if tipo_ingreso:
                ingresos_pareja=actualizar_ingresos(declaracion)
                
                ingresos_declaracion_data = {
                    'ingreso_mensual_pareja_dependientes': ingresos_pareja,
                    'ingreso_mensual_total':ingresos_pareja
                }
            observaciones_data = {}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        ingresos_declaracion_forms =IngresosDeclaracionForm(
            prefix='ingresos_declaracion', 
            initial=ingresos_declaracion_data)
        observaciones_form = ObservacionesForm(
            prefix="observaciones",
            initial=observaciones_data)

        if folio_declaracion:
            try:
                declaracion2 = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()


        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo

        return render(request, self.template_name, {
            'folio_declaracion': folio_declaracion,
            'ingresos_declaracion_forms': ingresos_declaracion_forms,
            'observaciones': observaciones_form,
            'ingresos_pareja': ingresos_pareja,
            'avance':avance,
            'faltas':faltas,
            'current_url':current_url,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o'),
            'declaracion2':declaracion2,
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP,
            'declaracion': declaracion
            


        })

    @method_decorator(login_required(login_url='/login'))
    def post(self, request, *args, **kwargs):
        """
        Obtiene y calcula el avance de la declaración con los datos ingresados
        Redirecciona a la siguiente sección de la declaración
        """
        folio_declaracion = self.kwargs['folio']

        current_url = resolve(request.path_info).url_name
        seccion = Secciones.objects.filter(url=current_url).first()
        
        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo

        tipo_ingreso = True
        if current_url == 'ingresos-servidor-publico':
            tipo_ingreso = False

        avance, faltas = 0, None
        try:
            declaracion = validar_declaracion(request, folio_declaracion)
            avance, faltas = obtiene_avance(declaracion)
        except ObjectDoesNotExist as e:
            raise Http404()

        folio = uuid.UUID(folio_declaracion)
        declaracion = Declaraciones.objects.filter(folio=folio).first()

        ingresos_declaracion_data = IngresosDeclaracion.objects.filter(declaraciones=declaracion, tipo_ingreso=tipo_ingreso).first()
        if ingresos_declaracion_data:
            observaciones_data = ingresos_declaracion_data.observaciones
        else:
            ingresos_declaracion_data = None
            observaciones_data = None
        
        #Se asigna por formulario la información correspondiente
        ingresos_declaracion_form = IngresosDeclaracionForm(
            request.POST,
            prefix="ingresos_declaracion",
            instance=ingresos_declaracion_data)
        observaciones_form = ObservacionesForm(
            request.POST,
            prefix="observaciones",
            instance=observaciones_data)

        ingresos_declaracion_is_valid = ingresos_declaracion_form.is_valid()
        observaciones_is_valid = observaciones_form.is_valid()
        
        if (ingresos_declaracion_is_valid and observaciones_is_valid):
            aplica = no_aplica(request)
            observaciones = None
            
            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            if aplica:
                ingresos_declaracion = ingresos_declaracion_form.save(commit=False)
                observaciones = observaciones_form.save()
                
                if 'ingreso_declaracion-ingreso_anio_anterior' in request.POST:
                    ingreso_anterior = json.loads(request.POST.get('ingreso_declaracion-ingreso_anio_anterior').lower())
                else:
                    ingreso_anterior = False
                
                if request.POST.get('ingresos_declaracion-ingreso_mensual_total') is None or ingresos_declaracion.ingreso_mensual_total is None:
                    ingresos_declaracion.ingreso_mensual_total = 0

                if request.POST.get('ingresos_declaracion-ingreso_mensual_neto') is None or ingresos_declaracion.ingreso_mensual_neto is None:
                    ingresos_declaracion.ingreso_mensual_neto = 0

                if request.POST.get('ingresos_declaracion-ingreso_mensual_cargo') is None or ingresos_declaracion.ingreso_mensual_cargo is None:
                    ingresos_declaracion.ingreso_mensual_cargo = 0
                    
                ingresos_declaracion.declaraciones = declaracion
                ingresos_declaracion.observaciones = observaciones
                ingresos_declaracion.tipo_ingreso = tipo_ingreso
                ingresos_declaracion.ingreso_anio_anterior = ingreso_anterior
                ingresos_declaracion.save()


            status, status_created = guardar_estatus(
                request,
                declaracion.folio,
                SeccionDeclaracion.COMPLETA,
                aplica=aplica,
                observaciones=observaciones)

            #Se valida que se completen los datos obligatorios
            seccion_dec = SeccionDeclaracion.objects.get(pk=status.id)
            if seccion_dec.num == 0:
                seccion_dec.num = 1

            faltantes = seccion_dec.max/seccion_dec.num
            if faltantes != 1.0:
               # ToDo error link? //  messages.warning(request, u"Algunos campos obligatorios de la sección no se completaron pero los datos han sido guardados, favor de completar información más tarde")
                return redirect('declaracion:ingresos-netos',folio=folio_declaracion)

            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')


            if current_url == 'ingresos-servidor-publico':
                if puesto >settings.LIMIT_DEC_SIMP:
                    return HttpResponseRedirect(
                        reverse_lazy('declaracion:bienes-inmuebles',
                                     args=[folio_declaracion]))
                else:
                    return HttpResponseRedirect(
                        reverse_lazy('declaracion:confirmar-allinone',
                                     args=[folio_declaracion]))
            else:
                if puesto >settings.LIMIT_DEC_SIMP:
                    if declaracion.cat_tipos_declaracion_id is not 1:
                        return HttpResponseRedirect(
                            reverse_lazy('declaracion:bienes-inmuebles',
                                         args=[folio_declaracion]))
                    else:
                        return HttpResponseRedirect(
                            reverse_lazy('declaracion:ingresos-servidor-publico',
                                         args=[folio_declaracion]))
                else:
                    if declaracion.cat_tipos_declaracion_id is not 1:
                        return HttpResponseRedirect(
                            reverse_lazy('declaracion:confirmar-allinone',
                                         args=[folio_declaracion]))
                    else:
                        return HttpResponseRedirect(
                            reverse_lazy('declaracion:ingresos-servidor-publico',
                                         args=[folio_declaracion]))


        return render(request, self.template_name, {
            'folio_declaracion': folio_declaracion,
            'ingresos_declaracion_forms': ingresos_declaracion_form,
            'observaciones': observaciones_form,
            'avance':avance,
            'faltas':faltas,
            'current_url':current_url,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o'),
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP
            


        })



