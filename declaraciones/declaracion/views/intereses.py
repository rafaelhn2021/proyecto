import uuid
from django.urls import reverse_lazy, resolve
from django.conf import settings
from django.views import View
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, Http404
from declaracion.models import (Declaraciones, SeccionDeclaracion,
                                EmpresasSociedades, Membresias, Apoyos,
                                InfoPersonalVar, Representaciones,
                                SociosComerciales, ClientesPrincipales,
                                BeneficiosGratuitos,
                                Secciones, SeccionDeclaracion, InfoPersonalFija)
from declaracion.forms import (ObservacionesForm,
                               DomiciliosForm, MembresiasForm,
                               RepresentacionesActivasForm,
                               SociosComercialesForm, ClientesPrincipalesForm,
                               BeneficiosGratuitosForm,
                               ApoyosForm, InfoPersonalVarForm)
from .utils import (guardar_estatus, no_aplica, declaracion_datos,
                    validar_declaracion,obtiene_avance,campos_configuracion)
from .declaracion import (DeclaracionDeleteView)
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages

class MembresiaDeleteView(DeclaracionDeleteView):
    """
    Class MembresiaDeleteView elimina los registros del modelo Membresias(Sección: ¿PARTICIPA EN LA TOMA DE DECISIONES DE ALGUNA DE ESTAS INSTITUCIONES ?)
    """
    model = Membresias


class MembresiaView(View):
    """
    Class MembresiaView vista basada en clases, carga y guardar Membresias(Sección: ¿PARTICIPA EN LA TOMA DE DECISIONES DE ALGUNA DE ESTAS INSTITUCIONES ?)
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/intereses/membresias.html'

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

        agregar, editar_id, membresia_data, informacion_registrada = (
            declaracion_datos(kwargs, Membresias, declaracion)
        )
        
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicipal
        if membresia_data:
            observaciones_data = membresia_data.observaciones
            domicilio_data = membresia_data.domicilios
            observaciones_data = model_to_dict(observaciones_data)
            domicilio_data = model_to_dict(domicilio_data)
            membresia_data = model_to_dict(membresia_data)
        else:
            observaciones_data = {}
            domicilio_data = {}
            membresia_data = {'moneda': 101}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        membresia_form = MembresiasForm(prefix="membresia",
                                       initial=membresia_data)
        observaciones_form = ObservacionesForm(prefix="observaciones",
                                               initial=observaciones_data)
        domicilio_form = DomiciliosForm(prefix="domicilio",
                                       initial=domicilio_data)

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
            'membresia_form': membresia_form,
            'observaciones_form': observaciones_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':avance,
            'faltas':faltas,
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

        agregar, editar_id, membresia_data, informacion_registrada = (
            declaracion_datos(kwargs, Membresias, declaracion)
        )

        if membresia_data:
            observaciones_data = membresia_data.observaciones
            domicilio_data = membresia_data.domicilios
        else:
            observaciones_data = None
            domicilio_data = None
            membresia_data = None
        
        #Se asigna por formulario la información correspondiente
        membresia_form = MembresiasForm(request.POST,
                                       prefix="membresia",
                                       instance=membresia_data)
        observaciones_form = ObservacionesForm(request.POST, prefix="observaciones",
                                               instance=observaciones_data)
        domicilio_form = DomiciliosForm(request.POST, prefix="domicilio",
                                       instance=domicilio_data)

        membresia_is_valid = membresia_form.is_valid()
        observaciones_is_valid = observaciones_form.is_valid()
        domicilio_is_valid = domicilio_form.is_valid()

        if membresia_is_valid and observaciones_is_valid and domicilio_is_valid:
            aplica = no_aplica(request)
            observaciones = observaciones_form.save()
            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            if aplica:
                membresias = membresia_form.save(commit=False)
                domicilio = domicilio_form.save()

                membresias.declaraciones = declaracion
                membresias.observaciones = observaciones
                membresias.domicilios = domicilio
                membresias.save()

            if not agregar and not editar_id:
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
                    messages.warning(request, u"Algunos campos obligatorios de la sección no se completaron pero los datos han sido guardados, favor de completar información más tarde")
                    return redirect('declaracion:membresias',folio=folio_declaracion)

            if request.POST.get("accion") == "guardar_otro":
                return redirect('declaracion:membresias-agregar', folio=folio_declaracion)
            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')

            return HttpResponseRedirect(
                reverse_lazy('declaracion:apoyos',
                             args=[folio_declaracion]))

        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo


        return render(request, self.template_name, {
            'membresia_form': membresia_form,
            'observaciones_form': observaciones_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':declaracion.avance,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o'),
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP
            
        })


class ApoyosDeleteView(DeclaracionDeleteView):
    """
    Class ApoyosDeleteView elimina los registros de del modelo Apoyos
    """
    model = Apoyos


class ApoyosView(View):
    """
    Class ApoyosView vista basada en clases, carga y guardar Apoyos(Sección: Apoyos o beneficios)
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/intereses/apoyos.html'

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

        info_persona_var = InfoPersonalVar.objects.filter(declaraciones=declaracion).first()

        kwargs['beneficiario_infopersonalvar'] = info_persona_var
        agregar, editar_id, apoyos_data, informacion_registrada = (
            declaracion_datos(kwargs, Apoyos, declaracion)
        )
        
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicipal
        if apoyos_data:
            observaciones_data = apoyos_data.observaciones
            observaciones_data = model_to_dict(observaciones_data)
            apoyos_data = model_to_dict(apoyos_data)
            beneficiario_data = model_to_dict(info_persona_var)
        else:
            observaciones_data = {}
            apoyos_data = {'moneda':101}
            beneficiario_data = {}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        apoyos_form = ApoyosForm(prefix="apoyos", initial=apoyos_data)
        observaciones_form = ObservacionesForm(prefix="observaciones", initial=observaciones_data)
        beneficiario_form = InfoPersonalVarForm(prefix="var", initial=beneficiario_data)

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
            'apoyos_form': apoyos_form,
            'beneficiario_form': beneficiario_form,
            'observaciones_form': observaciones_form,
            'folio_declaracion': folio_declaracion,
            'avance':avance,
            'faltas':faltas,
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

        info_persona_var = InfoPersonalVar.objects.filter(declaraciones=declaracion).first()

        agregar, editar_id, apoyos_data, informacion_registrada = (
            declaracion_datos(kwargs, Apoyos, declaracion)
        )

        if apoyos_data:
            observaciones_data = apoyos_data.observaciones
        else:
            observaciones_data = None
            apoyos_data = None
        
        #Se asigna por formulario la información correspondiente
        apoyos_form = ApoyosForm(request.POST, prefix="apoyos",
                                 instance=apoyos_data)
        observaciones_form = ObservacionesForm(request.POST,
                                               prefix="observaciones",
                                               instance=observaciones_data)

        apoyos_is_valid = apoyos_form.is_valid()
        observaciones_is_valid = observaciones_form.is_valid()

        if apoyos_is_valid and observaciones_is_valid:
            aplica = no_aplica(request)
            observaciones = observaciones_form.save()
            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            if aplica:
                apoyos = apoyos_form.save(commit=False)
                apoyos.beneficiario_infopersonalvar = info_persona_var
                apoyos.declaraciones = declaracion
                apoyos.observaciones = observaciones
                apoyos.save()

            if not agregar and not editar_id:
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
                    messages.warning(request, u"Algunos campos obligatorios de la sección no se completaron pero los datos han sido guardados, favor de completar información más tarde")
                    return redirect('declaracion:apoyos',folio=folio_declaracion)

            if request.POST.get("accion") == "guardar_otro":
                return redirect('declaracion:apoyos-agregar',
                                folio=folio_declaracion)
            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')

            return HttpResponseRedirect(
                reverse_lazy('declaracion:representacion-activa',
                             args=[folio_declaracion]))

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo

        return render(request, self.template_name, {
            'apoyos_form': apoyos_form,
            'observaciones_form': observaciones_form,
            'folio_declaracion': folio_declaracion,
            'avance':declaracion.avance,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP
            
        })


class RepresentacionesActivasDeleteView(DeclaracionDeleteView):
    """
    Class RepresentacionesActivasDeleteView elimina los registros de del modelo Representaciones
    """
    model = Representaciones


class RepresentacionesActivasView(View):
    """
    Class RepresentacionesActivasView vista basada en clases, carga y guardar Representación
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/intereses/representaciones-activas.html'

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

        kwargs['es_representacion_activa'] = 1
        agregar, editar_id, representaciones_activas_data, informacion_registrada = (
            declaracion_datos(kwargs, Representaciones, declaracion)
        )
        
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicipal
        if representaciones_activas_data:
            observaciones_data = representaciones_activas_data.observaciones
            info_personal_var_data = representaciones_activas_data.info_personal_var
            domicilio_data = info_personal_var_data.domicilios
            observaciones_data = model_to_dict(observaciones_data)
            representaciones_activas_data = model_to_dict(representaciones_activas_data)
            info_personal_var_data = model_to_dict(info_personal_var_data)
            domicilio_data = model_to_dict(domicilio_data)
        else:
            observaciones_data = {}
            representaciones_activas_data = {'pagado':0,'cat_moneda':101}
            info_personal_var_data = {'cat_entidades_federativas':14}
            domicilio_data = {}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        info_personal_var_form = InfoPersonalVarForm(
            prefix="var",
            initial=info_personal_var_data)
        representaciones_activas_form = RepresentacionesActivasForm(
            prefix="representaciones_activas",
            initial=representaciones_activas_data)
        observaciones_form = ObservacionesForm(
            prefix="observaciones",
            initial=observaciones_data)
        domicilio = DomiciliosForm(prefix="domicilio",
                                  initial=domicilio_data)

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
            'representaciones_activas_form': representaciones_activas_form,
            'observaciones_form': observaciones_form,
            'info_personal_var_form': info_personal_var_form,
            'folio_declaracion': folio_declaracion,
            'domicilio_form': domicilio,
            'avance':avance,
            'faltas':faltas,
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

        kwargs['es_representacion_activa'] = 1
        agregar, editar_id, representaciones_activas_data, informacion_registrada = (
            declaracion_datos(kwargs, Representaciones, declaracion)
        )
        
        if representaciones_activas_data:
            observaciones_data = representaciones_activas_data.observaciones
            info_personal_var_data = representaciones_activas_data.info_personal_var
            domicilio_data = info_personal_var_data.domicilios
        else:
            observaciones_data = None
            representaciones_activas_data = None
            info_personal_var_data = None
            domicilio_data = None
        
        #Se asigna por formulario la información correspondiente
        representaciones_activas_form = RepresentacionesActivasForm(
            request.POST,
            prefix="representaciones_activas",
            instance=representaciones_activas_data)
        info_personal_var_form = InfoPersonalVarForm(
            request.POST,
            prefix="var",
            instance=info_personal_var_data)
        observaciones_form = ObservacionesForm(
            request.POST,
            prefix="observaciones",
            instance=observaciones_data)
        domicilio_form = DomiciliosForm(request.POST, prefix="domicilio",
                                       instance=domicilio_data)

        representaciones_activas_is_valid = representaciones_activas_form.is_valid()
        observaciones_is_valid = observaciones_form.is_valid()
        info_personal_var_is_valid = info_personal_var_form.is_valid()
        domicilio_is_valid = domicilio_form.is_valid()

        if (representaciones_activas_is_valid and
            observaciones_is_valid and 
            info_personal_var_is_valid and
            domicilio_is_valid):

            aplica = no_aplica(request)
            observaciones = observaciones_form.save()
            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            if aplica:
                representaciones_activas = representaciones_activas_form.save(commit=False)
                
                info_personal_var = info_personal_var_form.save(commit=False)
                info_personal_var.declaraciones = declaracion
                domicilio = domicilio_form.save()
                info_personal_var.domicilios = domicilio
                info_personal_var.save()
                representaciones_activas.declaraciones = declaracion
                representaciones_activas.observaciones = observaciones
                representaciones_activas.info_personal_var = info_personal_var
                representaciones_activas.es_representacion_activa = 1

                representaciones_activas.save()

            if not agregar and not editar_id:
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
                    messages.warning(request, u"Algunos campos obligatorios de la sección no se completaron pero los datos han sido guardados, favor de completar información más tarde")
                    return redirect('declaracion:representacion-activa',folio=folio_declaracion)

            if request.POST.get("accion") == "guardar_otro":
                return redirect('declaracion:representacion-activa-agregar',
                                folio=folio_declaracion)
            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')

            return HttpResponseRedirect(
                reverse_lazy('declaracion:clientes-principales',
                             args=[folio_declaracion]))

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo

        return render(request, self.template_name, {
            'representaciones_activas_form': representaciones_activas_form,
            'domicilio_form': domicilio_form,
            'observaciones_form': observaciones_form,
            'info_personal_var_form': info_personal_var_form,
            'folio_declaracion': folio_declaracion,
            'avance':declaracion.avance,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP
            
        })


class SociosComercialesDeleteView(DeclaracionDeleteView):
    """
    Class SociosComercialesDeleteView elimina los registros de del modelo SociosComerciales
    """
    model = SociosComerciales


class SociosComercialesView(View):
    """
    Class SociosComercialesView vista basada en clases, carga y guardar Socios Comerciales(Sección: Participación en empresas, sociedades o asociaciones)
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/intereses/socios-comerciales.html'

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

        agregar, editar_id, socios_comerciales_data, informacion_registrada = (
            declaracion_datos(kwargs, SociosComerciales, declaracion)
        )
        
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicipal
        if socios_comerciales_data:
            observaciones_data = socios_comerciales_data.observaciones
            socio_infopersonalvar_data =  socios_comerciales_data.socio_infopersonalvar
            socio_infopersonalvar_data = model_to_dict(socio_infopersonalvar_data)
            observaciones_data = model_to_dict(observaciones_data)
            socios_comerciales_data = model_to_dict(socios_comerciales_data)
        else:
            observaciones_data = {}
            socios_comerciales_data = {'recibeRemuneracion': False,'montoMensual':0,'moneda':101}
            socio_infopersonalvar_data = {'cat_entidades_federativas': 14}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        socios_comerciales_form = SociosComercialesForm(
            prefix="socios_comerciales",
            initial=socios_comerciales_data)
        socio_infopersonalvar_form = InfoPersonalVarForm(
            prefix="var",
            initial=socio_infopersonalvar_data)
        observaciones_form = ObservacionesForm(
            prefix="observaciones",
            initial=observaciones_data)

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
            'socios_comerciales_form': socios_comerciales_form,
            'observaciones_form': observaciones_form,
            'socio_infopersonalvar_form': socio_infopersonalvar_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':avance,
            'faltas':faltas,
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

        agregar, editar_id, socios_comerciales_data, informacion_registrada = (
            declaracion_datos(kwargs, SociosComerciales, declaracion)
        )

        if socios_comerciales_data:
            observaciones_data = socios_comerciales_data.observaciones
            socio_infopersonalvar_data = socios_comerciales_data.socio_infopersonalvar
        else:
            observaciones_data = None
            socios_comerciales_data = None
            socio_infopersonalvar_data = None
        
        #Se asigna por formulario la información correspondiente
        socios_comerciales_form = SociosComercialesForm(
            request.POST,
            prefix="socios_comerciales",
            instance=socios_comerciales_data)
        socio_infopersonalvar_form = InfoPersonalVarForm(
            request.POST,
            prefix="var",
            instance=socio_infopersonalvar_data)
        observaciones_form = ObservacionesForm(
            request.POST,
            prefix="observaciones",
            instance=observaciones_data)

        socios_comerciales_is_valid = socios_comerciales_form.is_valid()
        observaciones_is_valid = observaciones_form.is_valid()
        socio_infopersonalvar_is_valid = socio_infopersonalvar_form.is_valid()

        if (socios_comerciales_is_valid and observaciones_is_valid and
            socio_infopersonalvar_is_valid):
            aplica = no_aplica(request)
            observaciones = observaciones_form.save()
            
            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            if aplica:
                socios_comerciales = socios_comerciales_form.save(commit=False)

                socio_infopersonalvar = socio_infopersonalvar_form.save(commit=False)
                socio_infopersonalvar.declaraciones = declaracion
                socio_infopersonalvar.save()

                socios_comerciales.socio_infopersonalvar = socio_infopersonalvar
                socios_comerciales.declaraciones = declaracion
                socios_comerciales.observaciones = observaciones
                socios_comerciales.save()

            if not agregar and not editar_id:
                status, status_created = guardar_estatus(request,
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
                    messages.warning(request, u"Algunos campos obligatorios de la sección no se completaron pero los datos han sido guardados, favor de completar información más tarde")
                    return redirect('declaracion:socios-comerciales',folio=folio_declaracion)


            if request.POST.get("accion") == "guardar_otro":
                return redirect('declaracion:socios-comerciales-agregar', folio=folio_declaracion)
            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')

            return HttpResponseRedirect(
                reverse_lazy('declaracion:membresias',
                             args=[folio_declaracion]))
        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo

        return render(request, self.template_name, {
            'socios_comerciales_form': socios_comerciales_form,
            'observaciones_form': observaciones_form,
            'socio_infopersonalvar_form': socio_infopersonalvar_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':declaracion.avance,
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP
            
        })


class ClientesPrincipalesDeleteView(DeclaracionDeleteView):
    """
    Class ClientesPrincipalesDeleteView elimina los registros de del modelo ClientesPrincipales
    """
    model = ClientesPrincipales


class ClientesPrincipalesView(View):
    """
    Class ClientesPrincipalesView vista basada en clases, carga y guardar Clientes principales
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/intereses/clientes-principales.html'

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        """
        Una sección puede estar conformado por más de un modelo y un formulario
        Se inicializan algunos campos con valores predeterminados, frecuentemente serán moneda y entidad federativa
        """
        folio_declaracion = self.kwargs['folio']
        avance, faltas =  0,None
        try:
            declaracion = validar_declaracion(request, folio_declaracion)
            avance, faltas = obtiene_avance(declaracion)
        except:
            raise Http404()

        agregar, editar_id, clientes_principales_data, informacion_registrada = (
            declaracion_datos(kwargs, ClientesPrincipales, declaracion)
        )
         
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicipal
        if clientes_principales_data:
            observaciones_data = clientes_principales_data.observaciones
            info_personal_var_data = clientes_principales_data.info_personal_var
            domicilio_data = info_personal_var_data.domicilios
            if domicilio_data:
                domicilio_data = model_to_dict(domicilio_data)
            else:
                domicilio_data = {}
            info_personal_var_data = model_to_dict(info_personal_var_data)
            observaciones_data = model_to_dict(observaciones_data)
            clientes_principales_data = model_to_dict(clientes_principales_data)
        else:
            observaciones_data = {}
            domicilio_data = {}
            clientes_principales_data = {"moneda":101}
            info_personal_var_data = {}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        clientes_principales_form = ClientesPrincipalesForm(
            prefix="clientes_principales",
            initial=clientes_principales_data)
        info_personal_var_form = InfoPersonalVarForm(
            prefix="var",
            initial=info_personal_var_data)
        domicilio_form = DomiciliosForm(
            prefix="domicilio",
            initial=domicilio_data)
        observaciones_form = ObservacionesForm(
            prefix="observaciones",
            initial=observaciones_data)

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
            'clientes_principales_form': clientes_principales_form,
            'observaciones_form': observaciones_form,
            'info_personal_var_form': info_personal_var_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':avance,
            'faltas':faltas,
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

        agregar, editar_id, clientes_principales_data, informacion_registrada = (
            declaracion_datos(kwargs, ClientesPrincipales, declaracion)
        )

        if clientes_principales_data:
            observaciones_data = clientes_principales_data.observaciones
            info_personal_var_data = clientes_principales_data.info_personal_var
            domicilio_data = info_personal_var_data.domicilios
        else:
            observaciones_data = None
            domicilio_data = None
            clientes_principales_data = None
            info_personal_var_data = None
        
        #Se asigna por formulario la información correspondiente
        clientes_principales_form = ClientesPrincipalesForm(
            request.POST,
            prefix="clientes_principales",
            instance=clientes_principales_data)
        info_personal_var_form = InfoPersonalVarForm(
            request.POST,
            prefix="var",
            instance=info_personal_var_data)
        domicilio_form = DomiciliosForm(
            request.POST,
            prefix="domicilio",
            instance=domicilio_data)
        observaciones_form = ObservacionesForm(
            request.POST,
            prefix="observaciones",
            instance=observaciones_data)

        clientes_principales_is_valid = clientes_principales_form.is_valid()
        domicilio_is_valid = domicilio_form.is_valid()
        observaciones_is_valid = observaciones_form.is_valid()
        info_personal_var_is_valid = info_personal_var_form.is_valid()

        if (clientes_principales_is_valid and
            domicilio_is_valid and
            observaciones_is_valid and
            info_personal_var_is_valid):

            aplica = no_aplica(request)
            observaciones = observaciones_form.save()
            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            if aplica:
                clientes_principales = clientes_principales_form.save(commit=False)
                domicilio = domicilio_form.save()
                info_personal_var = info_personal_var_form.save(commit=False)
                info_personal_var.razon_social = request.POST['var-razon_social']
                info_personal_var.declaraciones = declaracion
                info_personal_var.domicilios = domicilio
                info_personal_var.save()

                clientes_principales.info_personal_var = info_personal_var
                clientes_principales.declaraciones = declaracion
                clientes_principales.observaciones = observaciones

                clientes_principales.save()

            if not agregar and not editar_id:
                status, status_created = guardar_estatus(request,
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
                    messages.warning(request, u"Algunos campos obligatorios de la sección no se completaron pero los datos han sido guardados, favor de completar información más tarde")
                    return redirect('declaracion:clientes-principales',folio=folio_declaracion)

            if request.POST.get("accion") == "guardar_otro":
                return redirect('declaracion:clientes-principales-agregar', folio=folio_declaracion)
            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')

            return HttpResponseRedirect(
                reverse_lazy('declaracion:beneficios-gratuitos',
                             args=[folio_declaracion]))

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo

        return render(request, self.template_name, {
            'clientes_principales_form': clientes_principales_form,
            'observaciones_form': observaciones_form,
            'info_personal_var_form': info_personal_var_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':declaracion.avance,
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP
            
        })


class BeneficiosGratuitosDeleteView(DeclaracionDeleteView):
    """
    Class BeneficiosGratuitosDeleteView elimina los registros de del modelo BeneficiosGratuitos
    """
    model = BeneficiosGratuitos


class BeneficiosGratuitosView(View):
    """
    Class BeneficiosGratuitosView vista basada en clases, carga y guardar Beneficios gratuitos(Sección: Beneficios privados)
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/intereses/beneficios-gratuitos.html'

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

        agregar, editar_id, beneficios_gratuitos_data, informacion_registrada = (
            declaracion_datos(kwargs, BeneficiosGratuitos, declaracion)
        )
        
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicipal
        if beneficios_gratuitos_data:
            observaciones_data = beneficios_gratuitos_data.observaciones
            info_personal_var_data = beneficios_gratuitos_data.otorgante_infopersonalVar

            info_personal_var_data = model_to_dict(info_personal_var_data)
            beneficios_gratuitos_data = model_to_dict(beneficios_gratuitos_data)
            observaciones_data = model_to_dict(observaciones_data)
        else:
            observaciones_data = {}
            beneficios_gratuitos_data = {'moneda':101}
            info_personal_var_data = {}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        beneficios_gratuitos_form = BeneficiosGratuitosForm(
            prefix="beneficios_gratuitos",
            initial=beneficios_gratuitos_data)
        info_personal_var_form = InfoPersonalVarForm(
            prefix="var",
            initial=info_personal_var_data)
        observaciones_form = ObservacionesForm(
            prefix="observaciones",
            initial=observaciones_data)

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
            'beneficios_gratuitos_form': beneficios_gratuitos_form,
            'info_personal_var_form': info_personal_var_form,
            'observaciones_form': observaciones_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':avance,
            'faltas':faltas,
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

        agregar, editar_id, beneficios_gratuitos_data, informacion_registrada = (
            declaracion_datos(kwargs, BeneficiosGratuitos, declaracion)
        )

        if beneficios_gratuitos_data:
            observaciones_data = beneficios_gratuitos_data.observaciones
            info_personal_var_data = beneficios_gratuitos_data.otorgante_infopersonalVar
        else:
            observaciones_data = None
            beneficios_gratuitos_data = None
            info_personal_var_data = None
        
        #Se asigna por formulario la información correspondiente
        beneficios_gratuitos_form = BeneficiosGratuitosForm(
            request.POST,
            prefix="beneficios_gratuitos",
            instance=beneficios_gratuitos_data)
        info_personal_var_form = InfoPersonalVarForm(
            request.POST,
            prefix="var",
            instance=info_personal_var_data)
        observaciones_form = ObservacionesForm(
            request.POST,
            prefix="observaciones",
            instance=observaciones_data)

        beneficios_gratuitos_is_valid = beneficios_gratuitos_form.is_valid()
        observaciones_is_valid = observaciones_form.is_valid()

        if (beneficios_gratuitos_is_valid and
            observaciones_is_valid):
            aplica = no_aplica(request)
            observaciones = observaciones_form.save()
            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            if aplica:
                beneficios_gratuitos = beneficios_gratuitos_form.save(commit=False)
                info_personal_var = info_personal_var_form.save(commit=False)
                info_personal_var.declaraciones = declaracion
                info_personal_var.save()

                beneficios_gratuitos.declaraciones = declaracion
                beneficios_gratuitos.observaciones = observaciones
                beneficios_gratuitos.otorgante_infopersonalVar = info_personal_var

                beneficios_gratuitos.save()

            if not agregar and not editar_id:
                status, status_created = guardar_estatus(request,
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
                    messages.warning(request, u"Algunos campos obligatorios de la sección no se completaron pero los datos han sido guardados, favor de completar información más tarde")
                    return redirect('declaracion:beneficios-gratuitos',folio=folio_declaracion)

            if request.POST.get("accion") == "guardar_otro":
                return redirect('declaracion:beneficios-gratuitos-agregar', folio=folio_declaracion)
            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')

            return HttpResponseRedirect(
                reverse_lazy('declaracion:fideicomisos',
                             args=[folio_declaracion]))

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo

        
        return render(request, self.template_name, {
            'beneficios_gratuitos_form': beneficios_gratuitos_form,
            'info_personal_var_form': info_personal_var_form,
            'observaciones_form': observaciones_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':declaracion.avance,
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP
            
        })
