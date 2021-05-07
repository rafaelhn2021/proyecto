import uuid
from django.urls import reverse_lazy, resolve
from django.views import View
from django.shortcuts import render, redirect
from django.conf import settings
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, Http404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from declaracion.models import (Declaraciones, SeccionDeclaracion, DeudasOtros,
                                Secciones, SeccionDeclaracion,PrestamoComodato, InfoPersonalFija)
from declaracion.forms import (ObservacionesForm, DomiciliosForm, DeudasForm,
                               InfoPersonalVarForm,PrestamoComodatoForm)
from .utils import (actualizar_aplcia, guardar_estatus, no_aplica, declaracion_datos,
                    validar_declaracion,obtiene_avance,campos_configuracion)
from .declaracion import (DeclaracionDeleteView)
from django.contrib import messages

from declaracion.models.catalogos import (CatTiposMuebles,CatTiposInmuebles)
from api.serialize_functions import SECCIONES


class PrestamoComodatoDeleteView(DeclaracionDeleteView):
    """
    Class PrestamoComodatoDeleteView elimina los registros de del modelo PrestamoComoDato
    """
    model = PrestamoComodato
    seccion = "prestamocomodato"
    cat_tipos_inmueble = CatTiposInmuebles
    cat_tipos_muebles =  CatTiposMuebles

class PrestamoComodatoView(View):
    """
    Class PrestamoComodatoView vista basada en clases, carga y guardar PrestamoComoDato
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/pasivos/prestamoComodato.html'

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        """
        Una sección puede estar conformado por más de un modelo y un formulario
        Se inicializan algunos campos con valores predeterminados, frecuentemente serán moneda y entidad federativa
        """
        folio_declaracion = self.kwargs['folio']
        avance, faltas = 0,None
        
        try:
            declaracion = validar_declaracion(request, folio_declaracion)
            avance, faltas = obtiene_avance(declaracion)
        except:
            raise Http404()

        aplica = actualizar_aplcia(PrestamoComodato, declaracion, SECCIONES["PRESTAMO"])

        
        kwargs['prestamocomodato'] = True
        agregar, editar_id, comodato_data, informacion_registrada = (
            declaracion_datos(kwargs, PrestamoComodato, declaracion)
        )
        
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicpal
        if comodato_data:
            titular_infopersonalVar = comodato_data.titular_infopersonalVar
            observaciones_data = comodato_data.observaciones
            inmueble_domicilio_data = comodato_data.inmueble_domicilios

            observaciones_data = model_to_dict(observaciones_data)
            inmueble_domicilio_data = model_to_dict(inmueble_domicilio_data)
            titular_infopersonalVar = model_to_dict(titular_infopersonalVar)
            comodato_data = model_to_dict(comodato_data)
        else:
            comodato_data = {}
            titular_infopersonalVar = {}
            observaciones_data = {}   
            inmueble_domicilio_data = {'cat_entidades_federativas':14}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        prestamoComodato_Form = PrestamoComodatoForm(prefix="comodato", initial=comodato_data)
        observaciones_form = ObservacionesForm(prefix="observaciones",
                                               initial=observaciones_data)
        inmueble_domicilio_form = DomiciliosForm(prefix="inmueble_domicilio",
                                       initial=inmueble_domicilio_data)
        titular_infopersonalVar_form = InfoPersonalVarForm(
            prefix="titular_infopersonalVar",
            initial=titular_infopersonalVar)  # model name field titular_infoperosnalvar

        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','')
        current_url = current_url.replace('-editar','')
        current_url = current_url.replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        if folio_declaracion:
            try:
                declaracion2 = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()
        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo


        return render(request, self.template_name, {
            'prestamocomodato_form': prestamoComodato_Form,
            'observaciones_form': observaciones_form,
            'inmueble_domicilio_form': inmueble_domicilio_form,
            'titular_infopersonalVar_form': titular_infopersonalVar_form,
            'folio_declaracion': folio_declaracion,
            'avance':avance,
            'faltas':faltas,
            'aplica':aplica,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o'),
             'declaracion2':declaracion2,
             'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP

            })


    @method_decorator(login_required(login_url='/login'))
    def post(self, request, *args, **kwargs):
        """
        Obtiene y calcula el avance de la declaración con los datos ingresados
        Redirecciona a la siguiente sección de la declaración
        """
        folio_declaracion = self.kwargs['folio']
        tipo_comodato_form = request.POST.get('comodato-tipo_obj_comodato')
        prestamo_update = False

        try:
            declaracion = validar_declaracion(request, folio_declaracion)
        except:
            raise Http404()
        
        if 'pk' not in kwargs:
            kwargs['prestamocomodato'] = True
        else:
            prestamo_update = True

        agregar, editar_id, comodato_data, informacion_registrada = (
            declaracion_datos(kwargs, PrestamoComodato, declaracion)
        )
        
        if comodato_data:
            titular_infopersonalVar = comodato_data.titular_infopersonalVar
            observaciones_data = comodato_data.observaciones
            inmueble_domicilio_data = comodato_data.inmueble_domicilios
        else:
            comodato_data = None
            titular_infopersonalVar = None
            observaciones_data = None
            inmueble_domicilio_data = None
        
        if 'pk' in self.kwargs or comodato_data:
            if comodato_data.tipo_obj_comodato != tipo_comodato_form:
                messages.warning(request, u"El registro que desea actualizar es de tipo {} deberá eliminar el registro y/o crear uno de tipo {}".format(comodato_data.tipo_obj_comodato,tipo_comodato_form))
                return redirect('declaracion:prestamoComodato',folio=folio_declaracion)

        #Se asigna por formulario la información correspondiente
        prestamoComodato_form = PrestamoComodatoForm(request.POST, prefix="comodato", instance=comodato_data)
        observaciones_form = ObservacionesForm(request.POST, prefix="observaciones",
                                               instance=observaciones_data)
        inmueble_domicilio_form = DomiciliosForm(request.POST, prefix="inmueble_domicilio",
                                       instance=inmueble_domicilio_data)
        titular_infopersonalVar_form = InfoPersonalVarForm(request.POST, 
            prefix="titular_infopersonalVar",
            instance=titular_infopersonalVar)  
        
        observaciones_form_is_valid = observaciones_form.is_valid()
        inmueble_domicilio_form_is_valid = inmueble_domicilio_form.is_valid()
        titular_infopersonalVar_form_is_valid = titular_infopersonalVar_form.is_valid()
        prestamoComodato_form_is_valid = prestamoComodato_form.is_valid()
        aplica = no_aplica(request)
        observaciones = None

        if aplica:
            if (prestamoComodato_form_is_valid and 
                observaciones_form_is_valid and 
                inmueble_domicilio_form_is_valid and 
                titular_infopersonalVar_form_is_valid):

                campo_default_existente_m = PrestamoComodato.objects.filter(declaraciones=declaracion,campo_default=True,cat_tipos_muebles__isnull=False)
                campo_default_existente_in = PrestamoComodato.objects.filter(declaraciones=declaracion,campo_default=True,cat_tipos_inmueble__isnull=False)
                
                #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
                comodato = prestamoComodato_form.save(commit=False)

                #Se busca si existe algun registro creado por default para actualizar y no crear uno nuevo
                if tipo_comodato_form == 'INMUEBLE':
                    if len(campo_default_existente_in) > 0:
                        comodato.pk = campo_default_existente_in.first().id
                        comodato.campo_default = False
                        prestamo_update = True

                if tipo_comodato_form == 'MUEBLE':
                    if len(campo_default_existente_m) > 0:
                        comodato.id = campo_default_existente_m.first().id
                        comodato.campo_default = False
                        prestamo_update = True

                observaciones = observaciones_form.save()
                inmueble = inmueble_domicilio_form.save()
                titular = titular_infopersonalVar_form.save(commit=False)
                titular.declaraciones_id = declaracion.pk
                titular.save()
                
                comodato.observaciones = observaciones
                comodato.inmueble_domicilios = inmueble
                comodato.declaraciones = declaracion
                comodato.titular_infopersonalVar = titular
                comodato.save()

                if tipo_comodato_form == 'INMUEBLE':
                    if prestamo_update == False:
                        comodato_default_mueble = PrestamoComodato(
                            cat_tipos_muebles = CatTiposMuebles.objects.get(pk=9),
                            campo_default = True,
                            declaraciones= declaracion
                        )
                        comodato_default_mueble.save()

                if tipo_comodato_form == 'MUEBLE':
                    if prestamo_update == False:
                        comodato_default_inmueble = PrestamoComodato(
                            cat_tipos_inmueble = CatTiposInmuebles.objects.get(pk=9),
                            campo_default = True,
                            declaraciones= declaracion
                        )
                        comodato_default_inmueble.save()

        if not agregar and not editar_id:
            status, status_created = guardar_estatus(
                request,
                declaracion.folio,
                SeccionDeclaracion.COMPLETA,
                aplica=no_aplica(request))

            #Se valida que se completen los datos obligatorios
            seccion_dec = SeccionDeclaracion.objects.get(pk=status.id)
            if seccion_dec.num == 0:
                seccion_dec.num = 1

            faltantes = seccion_dec.max/seccion_dec.num
            if faltantes != 1.0:
                messages.warning(request, u"Algunos campos obligatorios de la sección no se completaron pero los datos han sido guardados, favor de completar información más tarde")
                return redirect('declaracion:prestamoComodato',folio=folio_declaracion)

        if request.POST.get("accion") == "guardar_otro":
            return redirect('declaracion:prestamoComodato-agregar', folio=folio_declaracion)
        if request.POST.get("accion") == "guardar_salir":
            return redirect('declaracion:perfil')

        return redirect('declaracion:socios-comerciales',
                        folio=folio_declaracion)

        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','')
        current_url = current_url.replace('-editar','')
        current_url = current_url.replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()


        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo

        return render(request, self.template_name, {
            'prestamocomodato_form': prestamoComodato_form,
            'observaciones_form': observaciones_form,
            'inmueble_domicilio_form': inmueble_domicilio_form,
            'titular_infopersonalVar_form': titular_infopersonalVar_form,
            'folio_declaracion': folio_declaracion,
            'avance':declaracion.avance,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o'),
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP



            })


class DeudasDeleteView(DeclaracionDeleteView):
    """
    Class DeudasDeleteView elimina los registros de del modelo DeudasOtros
    """
    model = DeudasOtros


class DeudasView(View):
    """
    Class DeudasView vista basada en clases, carga y guardar deudasotro
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/pasivos/deudas.html'

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        """
        Una sección puede estar conformado por más de un modelo y un formulario
        Se inicializan algunos campos con valores predeterminados, frecuentemente serán moneda y entidad federativa
        """
        folio_declaracion = self.kwargs['folio']
        avance, faltas = 0,None
        try:
            declaracion = validar_declaracion(request, folio_declaracion)
            avance, faltas = obtiene_avance(declaracion)
        except:
            raise Http404()
        aplica = actualizar_aplcia(DeudasOtros, declaracion, SECCIONES["ADEUDOS"])


        kwargs['cat_tipos_pasivos'] = 1
        agregar, editar_id, deudas_data, informacion_registrada = (
            declaracion_datos(kwargs, DeudasOtros, declaracion)
        )
        
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicpal
        if deudas_data:
            observaciones_data = deudas_data.observaciones
            tercero_infopersonalvar = deudas_data.tercero_infopersonalvar
            if tercero_infopersonalvar.domicilios:
                domicilio_data = tercero_infopersonalvar.domicilios
                domicilio_data = model_to_dict(domicilio_data)
            else:
                domicilio_data = {}
            tercero_infopersonalvar = model_to_dict(tercero_infopersonalvar)
            observaciones_data = model_to_dict(observaciones_data)
            deudas_data = model_to_dict(deudas_data)
        else:
            observaciones_data = {}
            domicilio_data = {}
            deudas_data = {}
            tercero_infopersonalvar = {}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        deudas_form = DeudasForm(prefix="deudas",
                                 initial=deudas_data)
        observaciones_form = ObservacionesForm(prefix="observaciones",
                                               initial=observaciones_data)
        domicilio_form = DomiciliosForm(prefix="domicilio",
                                       initial=domicilio_data)
        tercero_infopersonalvar_form = InfoPersonalVarForm(
            prefix="tercero_infopersonalvar",
            initial=tercero_infopersonalvar)

        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        if folio_declaracion:
            try:
                declaracion2 = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo


        return render(request, self.template_name, {
            'deudas_form': deudas_form,
            'observaciones_form': observaciones_form,
            'domicilio_form': domicilio_form,
            'tercero_infopersonalvar_form': tercero_infopersonalvar_form,
            'folio_declaracion': folio_declaracion,
            'avance':avance,
            'faltas':faltas,
            'aplica':aplica,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o'),
            'declaracion2':declaracion2,
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP

        })

    @method_decorator(login_required(login_url='/login'))
    def post(self, request, *args, **kwargs):
        """
        Obtiene y calcula el avance de la declaración con los datos ingresados
        Redirecciona a la siguiente sección de la declaración
        """
        folio_declaracion = self.kwargs['folio']
        try:
            declaracion = validar_declaracion(request, folio_declaracion)
        except:
            raise Http404()

        kwargs['cat_tipos_pasivos'] = 1
        agregar, editar_id, deudas_data, informacion_registrada = (
            declaracion_datos(kwargs, DeudasOtros, declaracion)
        )

        if deudas_data:
            observaciones_data = deudas_data.observaciones
            tercero_infopersonalvar = deudas_data.tercero_infopersonalvar
            if tercero_infopersonalvar.domicilios:
                domicilio_data = tercero_infopersonalvar.domicilios
            else:
                domicilio_data = None
        else:
            observaciones_data = None
            domicilio_data = None
            deudas_data = None
            tercero_infopersonalvar = None
        
        #Se asigna por formulario la información correspondiente
        deudas_form = DeudasForm(request.POST, prefix="deudas",
                                 instance=deudas_data)
        observaciones_form = ObservacionesForm(request.POST,
                                               prefix="observaciones",
                                               instance=observaciones_data)
        domicilio_form = DomiciliosForm(request.POST,
                                       prefix="domicilio",
                                       instance=domicilio_data)
        tercero_infopersonalvar_form = InfoPersonalVarForm(
            request.POST,
            prefix="tercero_infopersonalvar",
            instance=tercero_infopersonalvar)

        deudas_is_valid = deudas_form.is_valid()
        observaciones_is_valid = observaciones_form.is_valid()
        domicilio_is_valid = domicilio_form.is_valid()
        tercero_infopersonalvar_is_valid = tercero_infopersonalvar_form.is_valid()


        if (deudas_is_valid and
            observaciones_is_valid and
            domicilio_is_valid and
            tercero_infopersonalvar_is_valid):

            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            deudas = deudas_form.save(commit=False)
            observaciones = observaciones_form.save()
            domicilio = domicilio_form.save()

            tercero_infopersonalvar = tercero_infopersonalvar_form.save(commit=False)
            tercero_infopersonalvar.declaraciones = declaracion
            tercero_infopersonalvar.domicilios = domicilio
            tercero_infopersonalvar.save()

            deudas.tercero_infopersonalvar = tercero_infopersonalvar
            deudas.declaraciones = declaracion
            deudas.cat_tipos_pasivos_id = 1
            deudas.observaciones = observaciones
            deudas.save()

            if not agregar and not editar_id:
                status, status_created = guardar_estatus(
                    request,
                    declaracion.folio,
                    SeccionDeclaracion.COMPLETA,
                    aplica=no_aplica(request),
                    observaciones=observaciones)
                
                #Se valida que se completen los datos obligatorios
                seccion_dec = SeccionDeclaracion.objects.get(pk=status.id)
                if seccion_dec.num == 0:
                    seccion_dec.num = 1

                faltantes = seccion_dec.max/seccion_dec.num
                if faltantes != 1.0:
                    messages.warning(request, u"Algunos campos obligatorios de la sección no se completaron pero los datos han sido guardados, favor de completar información más tarde")
                    return redirect('declaracion:deudas',folio=folio_declaracion)

            if request.POST.get("accion") == "guardar_otro":
                return redirect('declaracion:deudas-agregar', folio=folio_declaracion)
            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')

            return redirect('declaracion:prestamoComodato',
                            folio=folio_declaracion)
        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo
        
        return render(request, self.template_name, {
            'deudas_form': deudas_form,
            'observaciones_form': observaciones_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
            'tercero_infopersonalvar_form': tercero_infopersonalvar_form,
            'avance':declaracion.avance,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o'),
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP

        })
