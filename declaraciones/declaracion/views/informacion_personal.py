import uuid
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.urls import reverse_lazy, resolve
from django.views import View
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from declaracion.models.informacion_personal import Nacionalidades
from declaracion.models import (Declaraciones, InfoPersonalFija,
                                InfoPersonalVar, SeccionDeclaracion,
                                DatosCurriculares, Encargos, ExperienciaLaboral,
                                ConyugeDependientes, Secciones, Apoyos,DeclaracionFiscal,CatCamposObligatorios,
                                IngresosDeclaracion, Domicilios)
from declaracion.models.catalogos import CatMonedas
from declaracion.forms import (DeclaracionForm, InfoPersonalFijaForm,
                               DomiciliosForm, InfoPersonalVarForm,
                               ObservacionesForm, DatosCurricularesForm,
                               DatosEncargoActualForm, ExperienciaLaboralForm,
                               ConyugeDependientesForm, ApoyosForm, ParejaForm, IngresosDeclaracionForm)
from .declaracion import (DeclaracionDeleteView)
from .utils import (guardar_estatus, declaracion_datos, validar_declaracion, obtiene_avance,
                    no_aplica,campos_configuracion,actualizar_ingresos,
                    get_declaracion_anterior)

from django.contrib.auth.models import User 
from declaracion.forms import RegistroForm,DeclaracionFiscalForm 
from django.contrib import messages
import os.path
from declaracion.models.catalogos import (CatMunicipios,CatTiposRelacionesPersonales, CatPaises, CatOrdenesGobierno, CatTiposDeclaracion)

from sitio.models import sitio_personalizacion, Valores_SMTP
from .mailto import mail_conf
from django.db.models import Q
from datetime import datetime, date


def listaMunicipios(request):
    """
    Función que se encarga de filtar los municipios de las entidades federativas
    """
    entidad_federativa = request.GET.get('entidad_federativa')
    municipios = CatMunicipios.objects.none()
    options = '<option value="" selected="selected">---------</option>'
    if entidad_federativa:
        municipios = CatMunicipios.objects.filter(cat_entidades_federativas=entidad_federativa)
    for municipio in municipios:
        options += '<option value="%s">%s</option>' % (
            municipio.pk,
            municipio.valor
        )
    response = {}
    response['municipios'] = options
    return JsonResponse(response)

class DeclaracionFiscalDelete(DeclaracionDeleteView):
    """
    Class DeclaracionFiscalDelete elimina los registros del modelo DeclaracionFiscal
    """
    model = DeclaracionFiscal

class DeclaracionFiscalFormView(View):
    """
    Class DeclaracionFiscalFormView vista basada en clases, carga y guardar declaración fiscal
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = "declaracion/declaracion-fiscal.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self,request,*args,**kwargs):
        """
        Una sección puede estar conformado por más de un modelo y un formulario
        Se inicializan algunos campos con valores predeterminados, frecuentemente serán moneda y entidad federativa
        """
        try:
            folio_declaracion = self.kwargs['folio']
            avance, faltas = 0,None
        except Exception as e:
            folio_declaracion = ''

        try:
            declaracion = validar_declaracion(request, folio_declaracion)
            avance, faltas = obtiene_avance(declaracion)
        except ObjectDoesNotExist as e:
            raise Http404()
        
        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        seccion_id = Secciones.objects.filter(url=current_url).first()
        seccion = SeccionDeclaracion.objects.filter(declaraciones=declaracion, seccion=seccion_id).first()
        
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicpal
        informacion_registrada = DeclaracionFiscal.objects.filter(declaraciones=declaracion)
        subir_archivo = True

        if informacion_registrada:
            subir_archivo =False


        if folio_declaracion:
            try:
                declaracion2 = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo


        declaracion_fiscal = DeclaracionFiscalForm(prefix='declaracion_fiscal')
        return render(request,self.template_name, {
            'folio_declaracion': folio_declaracion,
            'declaracion_fiscal':declaracion_fiscal,
            'informacion_registrada': informacion_registrada,
            'subir_archivo': subir_archivo,
            'avance':avance,
            'faltas':faltas,
            'declaracion2':declaracion2,
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP

        })
    
    @method_decorator(login_required(login_url='/login'))
    def post(self,request,*args,**kwargs):
        """
        Obtiene y calcula el avance de la declaración con los datos ingresados
        Redirecciona a la siguiente sección de la declaración
        """
        try:
            folio_declaracion = self.kwargs['folio']
        except Exception as e:
            folio_declaracion = None

        if folio_declaracion:
            try:
                declaracion = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()

        current_url = resolve(request.path_info).url_name
        seccion_id = Secciones.objects.filter(url=current_url).first()
        seccion = SeccionDeclaracion.objects.filter(declaraciones=declaracion, seccion=seccion_id).first()
        
        #Se asigna por formulario la información correspondiente(Aqui se manda un request,FILES debido al archivo que se sube)
        declaracion_fiscal = DeclaracionFiscalForm(self.request.POST,self.request.FILES,prefix='declaracion_fiscal')
        
        if declaracion_fiscal.is_valid():
            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            if no_aplica(request):
                fiscal = declaracion_fiscal.save(commit=False)            
                fiscal.declaraciones = declaracion
                fiscal.save()

            status_obj, status_created = guardar_estatus(request,
                                                         declaracion.folio,
                                                         SeccionDeclaracion.COMPLETA,
                                                         aplica=no_aplica(request))
            status_obj.save()
        
            informacion_registrada = DeclaracionFiscal.objects.filter(declaraciones=declaracion)
            subir_archivo = True

            if informacion_registrada:
                subir_archivo = False
            
            if request.POST.get("accion") == "guardar_salir":
                    return redirect('declaracion:perfil')

            return redirect('declaracion:confirmar-allinone',
                                folio=folio_declaracion)


        return render(request,self.template_name, {
            'folio_declaracion': folio_declaracion,
            'declaracion_fiscal':declaracion_fiscal,
            'informacion_registrada': informacion_registrada,
            'subir_archivo': subir_archivo,
            'avance': declaracion.avance
        })


class DeclaracionFormView(View):
    """
    Class DeclaracionFormView vista basada en clases, carga y guardar la declaración y de esta manera se inicializa el proceso de llenado de las demás secciones
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name="declaracion/informacion_personal/informacion-general.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self,request,*args,**kwargs):
        """
        Una sección puede estar conformado por más de un modelo y un formulario
        Se inicializan algunos campos con valores predeterminados, frecuentemente serán moneda y entidad federativa
        """
        usuario = request.user
        info_personal_var_data = {}
        avance,faltas = 0,None
        nueva_declaracion = False
        cat_tipos_declaracion_obj = None
        declaracion_obj = None
        declaracion2=None
        folio_declaracion = ''

        try:
            cat_tipos_declaracion = self.kwargs['cat_tipos_declaracion']
            cat_tipos_declaracion_obj = CatTiposDeclaracion.objects.get(pk=cat_tipos_declaracion)
            info_personal_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()

            info_personal_var_data = {
                'nombres': info_personal_fija.nombres,
                'apellido1': info_personal_fija.apellido1,
                'apellido2': info_personal_fija.apellido2,
                'rfc': info_personal_fija.rfc[:10],
                'homoclave':info_personal_fija.rfc[10:],
                'cat_pais': info_personal_fija.cat_pais,
                'curp': info_personal_fija.curp,
                'email': usuario.email,
                'email_personal': usuario.email,
            }
        except Exception as e:
            cat_tipos_declaracion = ''

        if 'folio' in self.kwargs:
            folio_declaracion = self.kwargs['folio']
        else:
            try:
                declaraciones_usuario = Declaraciones.objects.filter(info_personal_fija__usuario=usuario)
                declaracion_en_curso = declaraciones_usuario.filter(Q(cat_estatus__isnull=True) | Q(cat_estatus__pk__in=(1, 2, 3))).first()
                if declaracion_en_curso:
                    folio_declaracion = str(declaracion_en_curso.folio)
            except Exception as e:
                print('error-------------------------->', e)
                folio_declaracion = ''

        if folio_declaracion:
            try:
                declaracion_obj = validar_declaracion(request, folio_declaracion)
                avance, faltas = obtiene_avance(declaracion_obj)
            except ObjectDoesNotExist as e:
                raise Http404()

        #Obtiene la ultima declaración con la que se precargan los datos
        if cat_tipos_declaracion_obj and cat_tipos_declaracion_obj.codigo != 'INICIAL':
            declaracion_obj = Declaraciones.objects.filter(info_personal_fija=info_personal_fija).last()

        if declaracion_obj:
            info_personal_var_data = InfoPersonalVar.objects.filter(
                declaraciones=declaracion_obj).first()
            if info_personal_var_data.homoclave:
                homoclave = info_personal_var_data.homoclave
            else:
                homoclave = info_personal_var_data.rfc[10:]

            info_personal_var_data.homoclave = homoclave
            info_personal_var_data.rfc = info_personal_var_data.rfc[:10]

            observaciones_data = info_personal_var_data.observaciones
            info_personal_var_data = model_to_dict(info_personal_var_data)
            observaciones_data = model_to_dict(observaciones_data)
            declaracion_data = {'cat_tipos_declaracion': declaracion_obj.cat_tipos_declaracion}

            info_personal_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
            info_personal_fija_data = model_to_dict(info_personal_fija.usuario)
        else:
            observaciones_data = {}
            declaracion_data = {'cat_tipos_declaracion': cat_tipos_declaracion}
            info_personal_fija_data = {'email':usuario.email}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        declaracion = DeclaracionForm(prefix="declaracion",initial=declaracion_data)
        info_personal_var = InfoPersonalVarForm(prefix="var",
                                                initial=info_personal_var_data)
        observaciones = ObservacionesForm(prefix="observaciones",
                                  initial=observaciones_data)
        info_personal_fija = RegistroForm(prefix='info_personal_fija',
                                  initial=info_personal_fija_data)
        
        #Al momento de precargar se le asignan valores none a los ids de los objetos que se crearan
        if cat_tipos_declaracion_obj and cat_tipos_declaracion_obj.codigo != 'INICIAL':
            declaracion.pk = None
            info_personal_var.pk = None
            observaciones.pk = None
            folio_declaracion=''

        if isinstance(cat_tipos_declaracion, str):
            nueva_declaracion = True

            #Si ya se obtiene el folio de la declaración y se obtiene iinformacion de declaracion_onj
            #quiere decir que la declaración ya fue guardad como nueva pero con datos
            #de una declaración anterior
            if folio_declaracion != '' and declaracion_obj:
                nueva_declaracion = False
        else:
            nueva_declaracion =False

        #Se obtiene los campos que serán privados
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo


        if folio_declaracion:
            try:
                declaracion2 = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()

        return render(request,self.template_name, {
            'info_personal_fija': info_personal_fija,
            'declaracion': declaracion,
            'declaracion_previa': declaracion_obj,
            'info_personal_var': info_personal_var,
            'observaciones': observaciones,
            'folio_declaracion': folio_declaracion,
            'cat_tipos_declaracion': cat_tipos_declaracion,
            'cat_tipos_declaracion_obj': cat_tipos_declaracion_obj,
            'avance':avance,
            'faltas':faltas,
            'nueva_declaracion': nueva_declaracion,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o'),
            'declaracion2':declaracion2,
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP
        })

    @method_decorator(login_required(login_url='/login'))
    def post(self,request,*args,**kwargs):
        """
        Obtiene y calcula el avance de la declaración con los datos ingresados
        Redirecciona a la siguiente sección de la declaración
        """
        usuario = request.user
        avance, faltas = 0, None
        folio_declaracion = None
        
        try:
            cat_tipos_declaracion = self.kwargs['cat_tipos_declaracion']
        except Exception as e:
            cat_tipos_declaracion = None

        if 'folio' in self.kwargs:
            folio_declaracion = self.kwargs['folio']
        else:
            try:
                declaraciones_usuario = Declaraciones.objects.filter(info_personal_fija__usuario=usuario)
                declaracion_en_curso = declaraciones_usuario.filter(Q(cat_estatus__isnull=True) | Q(cat_estatus__pk__in=(1, 2, 3))).first()
                if declaracion_en_curso:
                    folio_declaracion = str(declaracion_en_curso.folio)
            except Exception as e:
                print('error-------------------------->', e)
                folio_declaracion = None

        if folio_declaracion:
            try:
                declaracion = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()

            info_personal_var_data = InfoPersonalVar.objects.filter(
                declaraciones=declaracion).first()
            observaciones_data = info_personal_var_data.observaciones
            info_personal_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
            info_personal_fija_data = model_to_dict(info_personal_fija.usuario)
        else:
            info_personal_var_data = None
            observaciones_data = None
            declaracion = None
            info_personal_fija_data = None
        
        #Se asigna por formulario la información correspondiente
        declaracion_form = DeclaracionForm(request.POST, prefix="declaracion",
                                           instance=declaracion)
        info_personal_var_form = InfoPersonalVarForm(request.POST, prefix="var",
                                                     instance=info_personal_var_data)
        observaciones_form = ObservacionesForm(request.POST, prefix="observaciones",
                                               instance=observaciones_data)
        info_personal_fija_form = RegistroForm(prefix='info_personal_fija',
                                  initial=info_personal_fija_data)

        declaracion_is_valid = declaracion_form.is_valid()
        info_personal_var_is_valid = info_personal_var_form.is_valid()
        observaciones_is_valid = observaciones_form.is_valid()

        if (declaracion_is_valid and
            info_personal_var_is_valid and
            observaciones_is_valid):


            try:
                cat_tipos_declaracion = self.kwargs['cat_tipos_declaracion']
            except Exception as e:
                cat_tipos_declaracion = None
            
            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            info_personal_var = info_personal_var_form.save(commit=False)
            observaciones = observaciones_form.save()

            info_personal_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
            info_personal_fija.cat_estados_civiles = info_personal_var.cat_estados_civiles
            info_personal_fija.cat_regimenes_matrimoniales = info_personal_var.cat_regimenes_matrimoniales
            info_personal_fija.num_id_identificacion = info_personal_var.num_id_identificacion
            info_personal_fija.email_personal = info_personal_var.email_personal
            info_personal_fija.tel_particular = info_personal_var.tel_particular
            info_personal_fija.tel_movil = info_personal_var.tel_movil
            info_personal_fija.usuario = request.user
            info_personal_fija.save()

            if not declaracion:
                declaraciones = declaracion_form.save(commit=False)
                declaraciones.cat_tipos_declaracion_id = cat_tipos_declaracion
            else:
                declaraciones = declaracion_form.save(commit=False)

            declaraciones.info_personal_fija = info_personal_fija
            declaraciones.save()

            info_personal_var.declaraciones = declaraciones
            info_personal_var.observaciones = observaciones
            info_personal_var.cat_tipo_persona_id = 1
            info_personal_var.rfc = u"{}{}".format(request.POST.get('var-rfc'), request.POST.get('var-homoclave'))
            info_personal_var.save()
            
            form_info_nacionalidades = info_personal_var_form.cleaned_data.get('nacionalidades')
            for nacion in form_info_nacionalidades:
                try:
                    nacionalidad_existente = Nacionalidades.objects.get(info_personal_var=info_personal_var, cat_paises=nacion)

                    if nacionalidad_existente is None:
                        nacionalidad = Nacionalidades(info_personal_var=info_personal_var, cat_paises=nacion)
                        nacionalidad.save()
                except Exception as e:
                    nacionalidad = Nacionalidades(info_personal_var=info_personal_var, cat_paises=nacion)
                    nacionalidad.save()
            
            # Actualiza la lista de nacionalidades
            if info_personal_var_data is not None:
                if form_info_nacionalidades.count() != info_personal_var_data.nacionalidades.count(): 
                    debug = ""
                    for pais in info_personal_var_data.nacionalidades.values():
                        if not pais in form_info_nacionalidades.values():
                            pais = pais.get("pais")
                            debug += u"No {} ".format(pais)
                            InfoPersonalVar.objects.filter(declaraciones=declaraciones).first().nacionalidades.remove(CatPaises.objects.filter(pais=pais).first())


            status, status_created = guardar_estatus(request,
                                           declaraciones.folio,
                                           SeccionDeclaracion.COMPLETA,
                                           observaciones=observaciones)

            if 'info_personal_fija-email' in request.POST:
                User.objects.filter(pk=request.user.id).update(email=request.POST['info_personal_fija-email'])

            
                
            try:
                info_per_f=InfoPersonalFija.objects.filter(usuario=usuario).first()
                sended=info_per_f.sended
                if sended is False:
                    smtp = Valores_SMTP.objects.filter(pk=1)

                    for s in smtp:
                        mailaddress = s.mailaddress
                        mailpassword = s.mailpassword
                        nombre_smtp = s.nombre_smtp
                        puerto = s.puerto

                    email=info_personal_var.email_personal

                    send_mail=mail_conf()
                    send_mail.mail_to_iniciar(email, info_personal_fija.nombres, info_personal_fija.nombre_ente_publico, mailaddress, mailpassword, nombre_smtp, puerto)
                    info_personal_fija.sended = True;
                    info_personal_fija.save();

            except Exception as e:
                print(str(e))


            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')

            return HttpResponseRedirect(
                reverse_lazy('declaracion:direccion',
                             args=[declaraciones.folio]))

        try:
            avance, faltas = obtiene_avance(declaracion)
        except Exception as e:
            avance = 0




        #Se obtiene los campos que serán privados
        current_url = resolve(request.path_info).url_name
        seccion = Secciones.objects.filter(url=current_url).first()

        return render(request,self.template_name, {
            'info_personal_fija': info_personal_fija_form,
            'declaracion': declaracion_form,
            'info_personal_var': info_personal_var_form,
            'observaciones': observaciones_form,
            'avance':avance,
            'folio_declaracion': folio_declaracion,
            'faltas':faltas,
            'cat_tipos_declaracion':cat_tipos_declaracion,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o')
        })

#Se separó el domicilio de la información personal var
class DomiciliosViews(View):
    """
    Class DomiciliosViews vista basada en clases, carga y guardar la dirección del declarante
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/informacion_personal/domicilio.html'

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args,**kwargs):
        folio_declaracion = self.kwargs['folio']
        avance,faltas=0,None
        declaracion_previa = False

        try:
            declaracion_obj = validar_declaracion(request, folio_declaracion)
            avance, faltas = obtiene_avance(declaracion_obj)
        except ObjectDoesNotExist as e:
            raise Http404()

        try:
            info_personal_var_data = InfoPersonalVar.objects.filter(declaraciones=declaracion_obj,cat_tipo_persona= 1).first()
        except ObjectDoesNotExist as e:
            info_personal_var_data = None
            raise Http404()

        # Busca información de una declaración previa si es de tipo MODIFICACIÓN/CONCLUSIÓN
        # Solo se obtiene información previa si la declaración actual aún no tiene registro de esta sección
        if declaracion_obj.cat_tipos_declaracion.codigo != 'INICIAL':
            if info_personal_var_data and not info_personal_var_data.domicilios:
                declaracion_obj = get_declaracion_anterior(declaracion_obj)

                if declaracion_obj:
                    declaracion_previa = True
                    info_personal_var_data = InfoPersonalVar.objects.filter(declaraciones=declaracion_obj,cat_tipo_persona= 1).first()

        # Si ya existe información se obtiene y separa la información necesaria
        # frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicpal
        if folio_declaracion:            
            if info_personal_var_data and info_personal_var_data.domicilios:
                domicilio_data = info_personal_var_data.domicilios
                domicilio_data = model_to_dict(domicilio_data)
            else:
                domicilio_data = {}                
        else:
            domicilio_data = {}

        domicilio = DomiciliosForm(prefix="domicilio",
                                  initial=domicilio_data)

        if declaracion_previa:
            domicilio.pk = None

        if folio_declaracion:
            try:
                declaracion2 = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo

        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        return render(request, self.template_name,{
            'form': domicilio,
            'folio_declaracion': folio_declaracion,
            'avance': avance,
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
        avance,faltas=0,None

        try:
            folio_declaracion = self.kwargs['folio']
        except Exception as e:
            folio_declaracion = None

        if folio_declaracion:
            try:
                declaracion = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()

            info_personal_var_data = InfoPersonalVar.objects.filter(declaraciones=declaracion,cat_tipo_persona= 1).first()
            domicilio_data = info_personal_var_data.domicilios
        else:
            domicilio_data = None
        
        #Se asigna por formulario la información correspondiente
        domicilio_form = DomiciliosForm(request.POST, prefix="domicilio", instance=domicilio_data)
        domicilio = domicilio_form
        domicilio_is_valid = domicilio_form.is_valid()

        if domicilio_is_valid:
            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            domicilio = domicilio_form.save()

            InfoPersonalVar.objects.filter(declaraciones=declaracion,cat_tipo_persona= 1).update(
                    domicilios=domicilio
                )

            status, status_created = guardar_estatus(
                request,
                declaracion.folio,
                SeccionDeclaracion.COMPLETA)

            #Se valida que se completen los datos obligatorios
            seccion_dec = SeccionDeclaracion.objects.get(pk=status.id)
            if seccion_dec.num == 0:
                seccion_dec.num = 1

            faltantes = seccion_dec.max/seccion_dec.num
            if faltantes != 1.0:
                messages.warning(request, u"Algunos campos obligatorios de la sección no se completaron pero los datos han sido guardados, favor de completar información más tarde")
                return redirect('declaracion:direccion',folio=folio_declaracion)


        
            if declaracion.cat_tipos_declaracion_id is not 1:
                aplica = no_aplica(request)
                observaciones_data = None
                observaciones_form = ObservacionesForm(
                    request.POST,
                    prefix="observaciones",
                    instance=observaciones_data)
                observaciones = observaciones_form.save()

                seccion_id = Secciones.objects.filter(url='ingresos-servidor-publico').first()
                declaraciones = Declaraciones.objects.filter(folio=folio_declaracion).first()
                tipo_ingreso=False
                try:
                    ingresos_declaracion_data = IngresosDeclaracion.objects.filter(declaraciones=declaracion, tipo_ingreso=tipo_ingreso).first()
                except Exception as e:
                    ingresos_declaracion_data = None
                if not ingresos_declaracion_data:

                    obj, created = IngresosDeclaracion.objects.update_or_create(
                        declaraciones=declaraciones,
                        tipo_ingreso=tipo_ingreso,
                        ingreso_anio_anterior=0,
                        ingreso_mensual_neto=0,
                        ingreso_mensual_total=0,
                        ingreso_mensual_cargo=0,
                        observaciones=observaciones
                    )
                
                try:
                    seccion_dec_id = SeccionDeclaracion.objects.filter(declaraciones=declaraciones, seccion=seccion_id).first()
                except Exception as e:
                    seccion_dec_id = None
                
                if seccion_dec_id:
                    seccion_dec_id.aplica=aplica
                    seccion_dec_id.estatus=SeccionDeclaracion.COMPLETA
                    seccion_dec_id.save()
                    obj=seccion_dec_id
                else:
                    obj, created = SeccionDeclaracion.objects.update_or_create(
                        declaraciones=declaraciones,
                        seccion=seccion_id,
                        defaults={'aplica': aplica, 'estatus': SeccionDeclaracion.COMPLETA},
                        observaciones=None
                    )

                #Se valida que se completen los datos obligatorios
                seccion_dec = SeccionDeclaracion.objects.get(pk=obj.id)
                if seccion_dec.num == 0:
                    seccion_dec.num = 1

            
            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')

            return HttpResponseRedirect(
                reverse_lazy('declaracion:datos-curriculares',
                             args=[folio_declaracion]))         
        try:
            avance,faltas = obtiene_avance(declaracion)
        except Exception as e:
            avance = 0

        #Se obtiene los campos que serán privados
        current_url = resolve(request.path_info).url_name
        seccion = Secciones.objects.filter(url=current_url).first()

        return render(request, self.template_name,{
            'form': domicilio,
            'folio_declaracion': folio_declaracion,
            'avance': avance,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o')
        })


class DatosCurricularesDelete(DeclaracionDeleteView):
    """
    Class DatosCurricularesDelete elimina los registros del modelo DatosCurriculares
    """
    model = DatosCurriculares


class DatosCurricularesView(View):
    """
    Class DatosCurricularesView vista basada en clases, carga y guardar los datos curriculares(escolares) del declarante
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/informacion_personal/datos-curriculares.html'

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args,**kwargs):
        """
        Una sección puede estar conformado por más de un modelo y un formulario
        Se inicializan algunos campos con valores predeterminados, frecuentemente serán moneda y entidad federativa
        """
        folio_declaracion = self.kwargs['folio']
        avance,faltas=0,None
        declaracion_previa = False

        try:
            declaracion = validar_declaracion(request, folio_declaracion)
            avance,faltas = obtiene_avance(declaracion)
        except ObjectDoesNotExist as e:
            raise Http404()

        agregar, editar_id, datos_curriculares_data, informacion_registrada = (
            declaracion_datos(kwargs, DatosCurriculares, declaracion)
        )
        
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicpal
        if datos_curriculares_data:
            observaciones_data = datos_curriculares_data.observaciones
            observaciones_data = model_to_dict(observaciones_data)
            datos_curriculares_data = model_to_dict(datos_curriculares_data)
        else:
            observaciones_data = {}
            datos_curriculares_data = {}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        datos_curriculares_form = DatosCurricularesForm(
            prefix="datos_curriculares",
            initial=datos_curriculares_data)
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


        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        return render(request, self.template_name, {
            'datos_curriculares_form': datos_curriculares_form,
            'observaciones_form': observaciones_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':declaracion.avance,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o'),
            'declaracion2':declaracion2,
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP
        })

    @method_decorator(login_required(login_url='/login'))
    def post(self, request, *args,**kwargs):
        """
        Obtiene y calcula el avance de la declaración con los datos ingresados
        Redirecciona a la siguiente sección de la declaración
        """
        folio_declaracion = self.kwargs['folio']
        try:
            declaracion = validar_declaracion(request, folio_declaracion)
        except ObjectDoesNotExist as e:
            raise Http404()

        agregar, editar_id, datos_curriculares_data, informacion_registrada = (
            declaracion_datos(kwargs, DatosCurriculares, declaracion)
        )

        if datos_curriculares_data:
            observaciones_data = datos_curriculares_data.observaciones
        else:
            observaciones_data = None
            datos_curriculares_data = None

        #Se asigna por formulario la información correspondiente
        datos_curriculares_form = DatosCurricularesForm(request.POST,
                                                        prefix="datos_curriculares",
                                                        instance=datos_curriculares_data)
        observaciones_form = ObservacionesForm(request.POST, prefix="observaciones",
                                               instance=observaciones_data)

        datos_curriculares_is_valid = datos_curriculares_form.is_valid()
        observaciones_is_valid = observaciones_form.is_valid()

        if datos_curriculares_is_valid and observaciones_is_valid:
            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            datos_curriculares = datos_curriculares_form.save(commit=False)
            observaciones = observaciones_form.save()

            datos_curriculares.declaraciones = declaracion
            datos_curriculares.observaciones = observaciones
            datos_curriculares.save()

            if not agregar and not editar_id:
                status, status_created = guardar_estatus(
                    request,
                    declaracion.folio,
                    SeccionDeclaracion.COMPLETA,
                    observaciones=observaciones)

                #Se valida que se completen los datos obligatorios
                seccion_dec = SeccionDeclaracion.objects.get(pk=status.id)
                if seccion_dec.num == 0:
                    seccion_dec.num = 1

                faltantes = seccion_dec.max/seccion_dec.num
                if faltantes != 1.0:
                    messages.warning(request, u"Algunos campos obligatorios de la sección no se completaron pero los datos han sido guardados, favor de completar información más tarde")
                    return redirect('declaracion:datos-curriculares',folio=folio_declaracion)

            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')
            if request.POST.get("accion") == "guardar_otro":
                return redirect('declaracion:datos-curriculares-agregar', folio=folio_declaracion)

            return HttpResponseRedirect(
                reverse_lazy('declaracion:datos-del-encargo-actual',
                             args=[folio_declaracion]))

        #Se obtiene los campos que serán privados
        current_url = resolve(request.path_info).url_name
        seccion = Secciones.objects.filter(url=current_url).first()

        return render(request, self.template_name, {
            'datos_curriculares_form': datos_curriculares_form,
            'observaciones_form': observaciones_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':declaracion.avance,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o')
        })

class DatosEncargoActualView(View):
    """
    Class DatosEncargoActualView vista basada en clases, carga y guardar información del cargo ya sea del declarante o algún dependiente
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/informacion_personal/datos-del-encargo-actual.html'

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        """
        Una sección puede estar conformado por más de un modelo y un formulario
        Se inicializan algunos campos con valores predeterminados, frecuentemente serán moneda y entidad federativa
        """
        folio_declaracion = self.kwargs['folio']
        avance, faltas = 0, None
        try:
            declaracion = validar_declaracion(request, folio_declaracion)
            avance, faltas = obtiene_avance(declaracion)
        except ObjectDoesNotExist as e:
            raise Http404()

        info_personal_fija_puesto = declaracion.info_personal_fija.cat_puestos
        datos_encargo_actual_data = Encargos.objects.filter(declaraciones=declaracion, cat_puestos__isnull=False,nivel_encargo__isnull=False).first()

        # Busca información de una declaración previa si es de tipo MODIFICACIÓN/CONCLUSIÓN
        # Solo se obtiene información previa si la declaración actual aún no tiene registro de esta sección
        if declaracion.cat_tipos_declaracion.codigo != 'INICIAL':
            if not datos_encargo_actual_data:
                declaracion = get_declaracion_anterior(declaracion)
                if declaracion:
                    datos_encargo_actual_data = Encargos.objects.filter(declaraciones=declaracion,cat_puestos__isnull=False,nivel_encargo__isnull=False).first()
                    if datos_encargo_actual_data:
                        datos_encargo_actual_data.pk = None
                        datos_encargo_actual_data.observaciones.pk = None
                        datos_encargo_actual_data.domicilios.pk = None

        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicpal
        try:
            personalizacion = sitio_personalizacion.objects.all()
        except Exception as e:
            personalizacion = None

        if not personalizacion or personalizacion is None:
            institucion = 'Secretaría ejecutiva'
        else:
            institucion = sitio_personalizacion.objects.first().nombre_institucion

        if datos_encargo_actual_data:
            puesto = datos_encargo_actual_data.cat_puestos

            datos_encargo_actual_data.nombre_ente_publico = institucion
            datos_encargo_actual_data.cat_areas = datos_encargo_actual_data.cat_puestos.cat_areas
            observaciones_data = datos_encargo_actual_data.observaciones
            domicilio_data = datos_encargo_actual_data.domicilios
            observaciones_data = model_to_dict(observaciones_data)
            datos_encargo_actual_data = model_to_dict(datos_encargo_actual_data)
            domicilio_data = model_to_dict(domicilio_data)

            datos_encargo_actual_data.update({'cat_areas': puesto.cat_areas.pk})
            datos_encargo_actual_data.update({'nivel_encargo': puesto.codigo})
        else:
            observaciones_data = {}
            datos_encargo_actual_data = {
                'nombre_ente_publico': institucion,
                'cat_ordenes_gobierno': 2,
                'cat_areas': info_personal_fija_puesto.cat_areas.pk, 
                'nivel_encargo': info_personal_fija_puesto.codigo, 
                'cat_puestos': info_personal_fija_puesto.pk
            }
            
            domicilio_data = {}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        datos_encargo_actual_form = DatosEncargoActualForm(
            prefix="datos_encargo_actual",
            initial=datos_encargo_actual_data)
        observaciones_form = ObservacionesForm(
            prefix="observaciones",
            initial=observaciones_data)
        domicilio_form = DomiciliosForm(
            prefix="domicilio",
            initial=domicilio_data)


        if folio_declaracion:
            try:
                declaracion2 = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo


        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()
        
        return render(request, self.template_name, {
            'datos_encargo_actual_form': datos_encargo_actual_form,
            'observaciones_form': observaciones_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
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
        folio_declaracion = self.kwargs['folio']

        try:
            declaracion = validar_declaracion(request, folio_declaracion)
        except:
            raise Http404()

        folio = uuid.UUID(folio_declaracion)
        declaracion = Declaraciones.objects.filter(folio=folio).first()
        datos_encargo_actual_data = Encargos.objects.filter(declaraciones=declaracion,cat_puestos__isnull=False,nivel_encargo__isnull=False).first()
        if datos_encargo_actual_data:
            observaciones_data = datos_encargo_actual_data.observaciones
            domicilio_data = datos_encargo_actual_data.domicilios
        else:
            observaciones_data = None
            datos_encargo_actual_data = None
            domicilio_data = None
        
        #Se asigna por formulario la información correspondiente
        datos_encargo_actual_form = DatosEncargoActualForm(
            request.POST,
            prefix="datos_encargo_actual",
            instance=datos_encargo_actual_data)
        observaciones_form = ObservacionesForm(
            request.POST,
            prefix="observaciones",
            instance=observaciones_data)
        domicilio_form = DomiciliosForm(
            request.POST,
            prefix="domicilio",
            instance=domicilio_data)

        if (datos_encargo_actual_form.is_valid() and
            observaciones_form.is_valid() and
            domicilio_form.is_valid()):

            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            datos_encargo_actual = datos_encargo_actual_form.save(commit=False)

            observaciones = observaciones_form.save()
            domicilio = domicilio_form.save()

            datos_encargo_actual.declaraciones = declaracion
            datos_encargo_actual.observaciones = observaciones
            datos_encargo_actual.domicilios = domicilio
            datos_encargo_actual.honorarios = request.POST.get('datos_encargo_actual-honorarios')
            if request.POST.get('datos_encargo_actual-cat_ordenes_gobierno') is None:
                datos_encargo_actual.cat_ordenes_gobierno = CatOrdenesGobierno.objects.get(pk=2)

            datos_encargo_actual.save()

            status, status_created = guardar_estatus(
                request,
                declaracion.folio,
                SeccionDeclaracion.COMPLETA,
                observaciones=observaciones)

            #Se valida que se completen los datos obligatorios
            seccion_dec = SeccionDeclaracion.objects.get(pk=status.id)
            if seccion_dec.num == 0:
                seccion_dec.num = 1

            faltantes = seccion_dec.max/seccion_dec.num
            if faltantes != 1.0:
                messages.warning(request, u"Algunos campos obligatorios de la sección no se completaron pero los datos han sido guardados, favor de completar información más tarde")
                return redirect('declaracion:datos-del-encargo-actual',folio=folio_declaracion)

            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')

            return HttpResponseRedirect(
                reverse_lazy('declaracion:experiencia-laboral',
                             args=[folio_declaracion]))

        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        return render(request, self.template_name, {
            'datos_encargo_actual_form': datos_encargo_actual_form,
            'observaciones_form': observaciones_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
            'avance':declaracion.avance,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o')
        })


class ExperienciaLaboralDeleteView(DeclaracionDeleteView):
    """
    Class ExperienciaLaboralDeleteView elimina los registros del modelo ExperienciaLaboral
    """
    model = ExperienciaLaboral


class ExperienciaLaboralView(View):
    """
    Class ExperienciaLaboralView vista basada en clases, carga y guardar experiencia laboral del declarante
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/informacion_personal/experiencia_laboral.html'

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        """
        Una sección puede estar conformado por más de un modelo y un formulario
        Se inicializan algunos campos con valores predeterminados, frecuentemente serán moneda y entidad federativa
        """
        folio_declaracion = self.kwargs['folio']
        avance, faltas = 0, None
        try:
            declaracion = validar_declaracion(request, folio_declaracion)
            avance, faltas = obtiene_avance(declaracion)
        except ObjectDoesNotExist as e:
            raise Http404()

        try:
            exp_laboral = ExperienciaLaboral.objects.filter(declaraciones=declaracion).first()
            
        except:
            exp_laboral = 0

        if exp_laboral:
            aplica=0
        else:
            aplica=1

        agregar, editar_id, experiencia_laboral_data, informacion_registrada = (
            declaracion_datos(kwargs, ExperienciaLaboral, declaracion)
        )
        
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicpal
        if experiencia_laboral_data:
            observaciones_data = experiencia_laboral_data.observaciones
            domicilio_data = experiencia_laboral_data.domicilios
            experiencia_laboral_data = model_to_dict(experiencia_laboral_data)
            observaciones_data = model_to_dict(observaciones_data)
            domicilio_data = model_to_dict(domicilio_data)
        else:
            experiencia_laboral_data = {}
            observaciones_data = {}
            domicilio_data = {}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        experiencia_laboral_form = ExperienciaLaboralForm(
            prefix="experiencia_laboral",
            initial=experiencia_laboral_data)
        observaciones_form = ObservacionesForm(
            prefix="observaciones",
            initial=observaciones_data)
        domicilio_form = DomiciliosForm(
            prefix="domicilio",
            initial=domicilio_data)


        if folio_declaracion:
            try:
                declaracion2 = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()
        
        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo

        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        return render(request, self.template_name, {
            'experiencia_laboral_form': experiencia_laboral_form,
            'observaciones_form': observaciones_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':declaracion.avance,
            'aplica':aplica,
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

        agregar, editar_id, experiencia_laboral_data, informacion_registrada = (
            declaracion_datos(kwargs, ExperienciaLaboral, declaracion)
        )

        if experiencia_laboral_data:
            observaciones_data = experiencia_laboral_data.observaciones
            domicilio_data = experiencia_laboral_data.domicilios
        else:
            experiencia_laboral_data = None
            observaciones_data = None
            domicilio_data = None
        
        #Se asigna por formulario la información correspondiente
        experiencia_laboral_form = ExperienciaLaboralForm(
            request.POST,
            prefix="experiencia_laboral",
            instance=experiencia_laboral_data)
        observaciones_form = ObservacionesForm(
            request.POST,
            prefix="observaciones",
            instance=observaciones_data)
        domicilio_form = DomiciliosForm(
            request.POST,
            prefix="domicilio",
            instance=domicilio_data)

        experiencia_laboral_is_valid = experiencia_laboral_form.is_valid()
        observaciones_is_valid = observaciones_form.is_valid()
        domicilio_is_valid = domicilio_form.is_valid()

        if (experiencia_laboral_is_valid and observaciones_is_valid and
            domicilio_is_valid):
            observaciones = None

            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            experiencia_laboral = experiencia_laboral_form.save(commit=False)
            observaciones = observaciones_form.save()
            domicilio = domicilio_form.save()

            experiencia_laboral.declaraciones = declaracion
            experiencia_laboral.observaciones = observaciones
            experiencia_laboral.domicilios = domicilio
            experiencia_laboral.save()

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
                    return redirect('declaracion:experiencia-laboral',folio=folio_declaracion)

            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')
            if request.POST.get("accion") == "guardar_otro":
                return redirect('declaracion:experiencia-laboral-agregar', folio=folio_declaracion)

            usuario = request.user
            info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
            puesto = info_per_fija.cat_puestos.codigo

            if puesto >settings.LIMIT_DEC_SIMP:
                return HttpResponseRedirect(
                    reverse_lazy('declaracion:datos-pareja',
                                 args=[folio_declaracion]))
            else:
                return HttpResponseRedirect(
                    reverse_lazy('declaracion:ingresos-netos',
                                 args=[folio_declaracion]))

        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        return render(request, self.template_name, {
            'experiencia_laboral_form': experiencia_laboral_form,
            'observaciones_form': observaciones_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':declaracion.avance,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o')
        })


class ParejaDeleteView(DeclaracionDeleteView):
    """
    Class ParejaDeleteView elimina los registros del modelo ConyugeDependientes
    """
    model = ConyugeDependientes

class ParejaView(View):
    """
    Class ExperienciaLaboralView vista basada en clases, carga y guardar información de la pareja/conyugue
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/informacion_personal/datos-pareja.html'

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
            avance, faltas =obtiene_avance(declaracion)
        except:
            raise Http404()
        
        datos_pareja_data = ConyugeDependientes.objects.filter(declaraciones=declaracion,es_pareja= 1).first()
        
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicpal
        if datos_pareja_data:
            observaciones_data = datos_pareja_data.observaciones
            info_personal_var_data = datos_pareja_data.dependiente_infopersonalvar
            actividad_laboral_sector_data = datos_pareja_data.actividadLaboralSector
            domiclios_data = info_personal_var_data.domicilios

            if domiclios_data:
                domiclios_data = model_to_dict(domiclios_data)
            else:
                domiclios_data = {}

            if actividad_laboral_sector_data:
                actividad_laboral_sector_data = model_to_dict(actividad_laboral_sector_data)
                actividad_laboral_sector_data["posesion_inicio_publico"] = actividad_laboral_sector_data["posesion_inicio"]
                actividad_laboral_sector_data["posesion_inicio_privado"] = actividad_laboral_sector_data["posesion_inicio"]
                actividad_laboral_sector_data["moneda_publico"] = actividad_laboral_sector_data["moneda"]
                actividad_laboral_sector_data["moneda_privado"] = actividad_laboral_sector_data["moneda"]
            else:
                actividad_laboral_sector_data = {}

            observaciones_data = model_to_dict(observaciones_data)
            info_personal_var_data = model_to_dict(info_personal_var_data)
            datos_pareja_data = model_to_dict(datos_pareja_data)
        else:
            domiclios_data = {}
            domiclios_actividad_laboral_sector_data = {}
            observaciones_data = {}
            datos_pareja_data = {}
            info_personal_var_data = {}
            actividad_laboral_sector_data = {'moneda':101}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        datos_pareja_form = ParejaForm(
            prefix="datos_pareja",
            initial=datos_pareja_data)
        info_personal_var_form = InfoPersonalVarForm(
            prefix="var",
            initial=info_personal_var_data)
        observaciones_form = ObservacionesForm(
            prefix="observaciones",
            initial=observaciones_data)
        domicilio_form = DomiciliosForm(
            prefix="domicilio",
            initial=domiclios_data)
        actividad_laboral_sector_form = DatosEncargoActualForm(
            prefix="datos_encargo_actual", 
            initial=actividad_laboral_sector_data)

        if folio_declaracion:
            try:
                declaracion2 = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo


        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()


        return render(request, self.template_name, {
            'actividad_laboral_sector_form': actividad_laboral_sector_form,
            'datos_pareja_form': datos_pareja_form,
            'observaciones_form': observaciones_form,
            'info_personal_var_form': info_personal_var_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
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

        datos_pareja_data = ConyugeDependientes.objects.filter(declaraciones=declaracion,es_pareja=1).first()

        if datos_pareja_data:
            observaciones_data = datos_pareja_data.observaciones
            info_personal_var_data = datos_pareja_data.dependiente_infopersonalvar
            domiclios_data = info_personal_var_data.domicilios
            actividad_laboral_sector_data = datos_pareja_data.actividadLaboralSector
        else:
            domiclios_data = None
            observaciones_data = None
            datos_pareja_data = None
            info_personal_var_data = None
            actividad_laboral_sector_data = None
        
        #Se asigna por formulario la información correspondiente
        datos_pareja_form = ParejaForm(
            request.POST,
            prefix="datos_pareja",
            instance=datos_pareja_data)
        observaciones_form = ObservacionesForm(
            request.POST,
            prefix="observaciones",
            instance=observaciones_data)
        info_personal_var_form = InfoPersonalVarForm(
            request.POST,
            prefix="var",
            instance=info_personal_var_data)
        domicilio_form = DomiciliosForm(
            request.POST,
            prefix="domicilio",
            instance=domiclios_data)
        actividad_laboral_sector_form = DatosEncargoActualForm(
            request.POST,
            prefix="datos_encargo_actual",
            instance=actividad_laboral_sector_data)
        
        if (datos_pareja_form.is_valid() and
            observaciones_form.is_valid() and
            info_personal_var_form.is_valid() and
            domicilio_form.is_valid() and 
            actividad_laboral_sector_form.is_valid()):

            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            datos_pareja = datos_pareja_form.save(commit=False)
            observaciones = observaciones_form.save()
            domicilio = domicilio_form.save()

            info_personal_var = info_personal_var_form.save(commit=False)
            info_personal_var.declaraciones = declaracion
            info_personal_var.domicilios = domicilio
            info_personal_var.cat_tipo_persona_id = 2
            info_personal_var.save()
            
            form_info_nacionalidades = info_personal_var_form.cleaned_data.get('nacionalidades')
            for nacion in form_info_nacionalidades:
                nacionalidad = Nacionalidades(info_personal_var=info_personal_var, cat_paises=nacion)
                nacionalidad.save()
            
            actividad_laboral_sector_var = actividad_laboral_sector_form.save(commit=False)
            actividad_laboral_sector_var.declaraciones = declaracion
            actividad_laboral_sector_var.domicilios = domicilio
            actividad_laboral_sector_var.salarioMensualNeto = 0

            if request.POST.get('datos_pareja-actividadLaboral') == '1':
                actividad_laboral_sector_var.posesion_inicio = date(int(request.POST.get('datos_encargo_actual-posesion_inicio_publico_year')),int(request.POST.get('datos_encargo_actual-posesion_inicio_publico_month')),int(request.POST.get('datos_encargo_actual-posesion_inicio_publico_day')))
                actividad_laboral_sector_var.moneda = CatMonedas.objects.get(pk= request.POST.get('datos_encargo_actual-moneda_publico')) 

                if request.POST.get('datos_encargo_actual-salarioMensualNetoPublico'):
                    actividad_laboral_sector_var.salarioMensualNeto = int(request.POST.get('datos_encargo_actual-salarioMensualNetoPublico'))
                    
            if request.POST.get('datos_pareja-actividadLaboral') == '2':
                actividad_laboral_sector_var.posesion_inicio = date(int(request.POST.get('datos_encargo_actual-posesion_inicio_privado_year')),int(request.POST.get('datos_encargo_actual-posesion_inicio_privado_month')),int(request.POST.get('datos_encargo_actual-posesion_inicio_privado_day')))
                actividad_laboral_sector_var.moneda = CatMonedas.objects.get(pk=request.POST.get('datos_encargo_actual-moneda_privado'))


                if request.POST.get('datos_encargo_actual-salarioMensualNetoPrivado'): 
                    actividad_laboral_sector_var.salarioMensualNeto = int(request.POST.get('datos_encargo_actual-salarioMensualNetoPrivado'))

                    
            actividad_laboral_sector_var.observaciones = observaciones
            actividad_laboral_sector_var.save()

            datos_pareja.declaraciones = declaracion
            datos_pareja.observaciones = observaciones

            declarante_infopersonalvar = InfoPersonalVar.objects.filter(
                declaraciones=declaracion).first()

            datos_pareja.declarante_infopersonalvar = declarante_infopersonalvar
            datos_pareja.dependiente_infopersonalvar = info_personal_var
            datos_pareja.actividadLaboralSector = actividad_laboral_sector_var
            datos_pareja.proveedor_contratista = bool(request.POST.get('conyuge_dependiente-proveedor_contratista'))
            datos_pareja.es_pareja = 1
            datos_pareja.save()

            monto = actualizar_ingresos(declaracion)

            try:
                ingreso=IngresosDeclaracion.objects.get(tipo_ingreso=1, declaraciones=declaracion)
                neto = ingreso.ingreso_mensual_neto
                ingreso.ingreso_mensual_pareja_dependientes=monto
                ingreso.ingreso_mensual_total=monto+neto
                ingreso.save()
            except Exception as e:
                print(e)

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
                return redirect('declaracion:datos-pareja',folio=folio_declaracion)

            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')

            return HttpResponseRedirect(
                reverse_lazy('declaracion:dependientes-economicos',
                             args=[folio_declaracion]))

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo

        
        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        return render(request, self.template_name, {
            'actividad_laboral_sector_form': actividad_laboral_sector_form,
            'datos_pareja_form': datos_pareja_form,
            'observaciones_form': observaciones_form,
            'info_personal_var_form': info_personal_var_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
            'avance':declaracion.avance,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o'),
            'puesto':puesto,
            'limit_simp':settings.LIMIT_DEC_SIMP
        })

class ConyugeDependientesDeleteView(DeclaracionDeleteView):
    """
    Class ConyugeDependientesDeleteView elimina los registros del modelo ConyugeDependientes
    """
    model = ConyugeDependientes


class ConyugeDependientesView(View):
    """
    Class ConyugeDependientesView vista basada en clases, carga y guardar información de los dependientes economicos(hijo, padre, abuelo)
    --------

    Methods
    -------
    get(self,request,*args,**kwargs)
        Obtiene la información inicial de la sección y carga los formularios necesarios para ser guardada

    post(self, request, *args, **kwargs)
        Recibe datos ingresados por el usario y son guardados en la base de datos por medio de ORM de Django

    """
    template_name = 'declaracion/informacion_personal/conyuge-dependiente.html'

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
            avance, faltas =obtiene_avance(declaracion)
        except:
            raise Http404()


        try:
            con_dep = ConyugeDependientes.objects.filter(declaraciones=declaracion,es_pareja= 0).first()
            
        except:
            con_dep = 0

        if con_dep:
            aplica=0
        else:
            aplica=1

        kwargs['es_pareja'] = 0
        agregar, editar_id, conyuge_dependiente_data, informacion_registrada = (
            declaracion_datos(kwargs, ConyugeDependientes, declaracion)
        )
        
        #Si ya existe información se obtiene y separa la información necesaria
        #frecuentemente observaciones y domicilio o demás datos que pertenezcan a otro formulario que no sea el prinicpal
        if conyuge_dependiente_data:
            observaciones_data = conyuge_dependiente_data.observaciones
            info_personal_var_data = conyuge_dependiente_data.dependiente_infopersonalvar
            actividad_laboral_sector_data = conyuge_dependiente_data.actividadLaboralSector
            domiclios_data = info_personal_var_data.domicilios

            if domiclios_data:
                domiclios_data = model_to_dict(domiclios_data)
            else:
                domiclios_data = {}

            if actividad_laboral_sector_data:
                actividad_laboral_sector_data = model_to_dict(actividad_laboral_sector_data)
                actividad_laboral_sector_data["posesion_inicio_publico"] = actividad_laboral_sector_data["posesion_inicio"]
                actividad_laboral_sector_data["posesion_inicio_privado"] = actividad_laboral_sector_data["posesion_inicio"]
                actividad_laboral_sector_data["moneda_publico"] = actividad_laboral_sector_data["moneda"]
                actividad_laboral_sector_data["moneda_privado"] = actividad_laboral_sector_data["moneda"]

            else:
                actividad_laboral_sector_data = {}

            observaciones_data = model_to_dict(observaciones_data)
            info_personal_var_data = model_to_dict(info_personal_var_data)
            conyuge_dependiente_data = model_to_dict(conyuge_dependiente_data)
        else:
            domiclios_data = {}
            domiclios_actividad_laboral_sector_data = {}
            observaciones_data = {}
            conyuge_dependiente_data = {}
            info_personal_var_data = {}
            actividad_laboral_sector_data = {'moneda':101}
        
        #Se inicializan los formularios a utilizar que conformen a la sección
        conyuge_dependiente_form = ConyugeDependientesForm(
            prefix="conyuge_dependiente",
            initial=conyuge_dependiente_data)
        info_personal_var_form = InfoPersonalVarForm(
            prefix="var",
            initial=info_personal_var_data)
        observaciones_form = ObservacionesForm(
            prefix="observaciones",
            initial=observaciones_data)
        domicilio_form = DomiciliosForm(
            prefix="domicilio",
            initial=domiclios_data)
        actividad_laboral_form = DatosEncargoActualForm(
            prefix="datos_encargo_actual", 
            initial=actividad_laboral_sector_data)

        if folio_declaracion:
            try:
                declaracion2 = validar_declaracion(request, folio_declaracion)
            except ObjectDoesNotExist as e:
                raise Http404()

        usuario = request.user
        info_per_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()
        puesto = info_per_fija.cat_puestos.codigo

        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        return render(request, self.template_name, {
            'actividad_laboral_sector_form': actividad_laboral_form,
            'conyuge_dependiente_form': conyuge_dependiente_form,
            'observaciones_form': observaciones_form,
            'info_personal_var_form': info_personal_var_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':avance,
            'aplica':aplica,
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
        kwargs['es_pareja'] = 0
        agregar, editar_id, conyuge_dependiente_data, informacion_registrada = (
            declaracion_datos(kwargs, ConyugeDependientes, declaracion)
        )

        if conyuge_dependiente_data:
            observaciones_data = conyuge_dependiente_data.observaciones
            info_personal_var_data = conyuge_dependiente_data.dependiente_infopersonalvar
            domiclios_data = info_personal_var_data.domicilios
            actividad_laboral_sector_data = conyuge_dependiente_data.actividadLaboralSector
        else:
            domiclios_data = None
            observaciones_data = None
            conyuge_dependiente_data = None
            info_personal_var_data = None
            actividad_laboral_sector_data = None
        
        #Se asigna por formulario la información correspondiente
        conyuge_dependiente_form = ConyugeDependientesForm(
            request.POST,
            prefix="conyuge_dependiente",
            instance=conyuge_dependiente_data)
        observaciones_form = ObservacionesForm(
            request.POST,
            prefix="observaciones",
            instance=observaciones_data)
        info_personal_var_form = InfoPersonalVarForm(
            request.POST,
            prefix="var",
            instance=info_personal_var_data)
        domicilio_form = DomiciliosForm(
            request.POST,
            prefix="domicilio",
            instance=domiclios_data)
        actividad_laboral_form = DatosEncargoActualForm(
            request.POST,
            prefix="datos_encargo_actual",
            instance=actividad_laboral_sector_data)

        if (conyuge_dependiente_form.is_valid() and
            observaciones_form.is_valid() and
            info_personal_var_form.is_valid() and
            domicilio_form.is_valid() and 
            actividad_laboral_form.is_valid()):

            aplica = no_aplica(request)
            observaciones = None

            #Se guarda individualmente los formularios para posteriormente integrar la información retornada al fomulario principal de la sección
            if aplica:
                conyuge_dependiente = conyuge_dependiente_form.save(commit=False)
                observaciones = observaciones_form.save()
                domicilio = domicilio_form.save()

                info_personal_var = info_personal_var_form.save(commit=False)
                info_personal_var.declaraciones = declaracion
                info_personal_var.domicilios = domicilio
                info_personal_var.cat_tipo_persona_id = 2
                info_personal_var.save()
                
                for nacion in info_personal_var_form.cleaned_data.get('nacionalidades'):
                    nacionalidad = Nacionalidades(info_personal_var=info_personal_var, cat_paises=nacion)
                    nacionalidad.save()
                
                actividad_laboral_var = actividad_laboral_form.save(commit=False)
                actividad_laboral_var.declaraciones = declaracion
                actividad_laboral_var.domicilios = domicilio
                actividad_laboral_var.observaciones = observaciones
                actividad_laboral_var.salarioMensualNeto = 0

                if request.POST.get('conyuge_dependiente-actividadLaboral') == '1':
                    actividad_laboral_var.posesion_inicio = date(int(request.POST.get('datos_encargo_actual-posesion_inicio_publico_year')),int(request.POST.get('datos_encargo_actual-posesion_inicio_publico_month')),int(request.POST.get('datos_encargo_actual-posesion_inicio_publico_day')))
                    actividad_laboral_var.moneda = CatMonedas.objects.get(pk= request.POST.get('datos_encargo_actual-moneda_publico')) 

                    if request.POST.get('datos_encargo_actual-salarioMensualNetoPublico'):
                        actividad_laboral_var.salarioMensualNeto = int(request.POST.get('datos_encargo_actual-salarioMensualNetoPublico'))
                        
                if request.POST.get('conyuge_dependiente-actividadLaboral') == '2':
                    actividad_laboral_var.posesion_inicio = date(int(request.POST.get('datos_encargo_actual-posesion_inicio_privado_year')),int(request.POST.get('datos_encargo_actual-posesion_inicio_privado_month')),int(request.POST.get('datos_encargo_actual-posesion_inicio_privado_day')))
                    actividad_laboral_var.moneda = CatMonedas.objects.get(pk=request.POST.get('datos_encargo_actual-moneda_privado'))
                    
                    if request.POST.get('datos_encargo_actual-salarioMensualNetoPrivado'):
                        actividad_laboral_var.salarioMensualNeto = int(request.POST.get('datos_encargo_actual-salarioMensualNetoPrivado'))

                actividad_laboral_var.observaciones = observaciones
                actividad_laboral_var.save()

                conyuge_dependiente.declaraciones = declaracion
                conyuge_dependiente.observaciones = observaciones

                declarante_infopersonalvar = InfoPersonalVar.objects.filter(
                    declaraciones=declaracion).first()

                conyuge_dependiente.declarante_infopersonalvar = declarante_infopersonalvar
                conyuge_dependiente.dependiente_infopersonalvar = info_personal_var
                conyuge_dependiente.actividadLaboralSector = actividad_laboral_var
                conyuge_dependiente.es_pareja = 0
                conyuge_dependiente.save()

                monto = actualizar_ingresos(declaracion)

                try:
                    ingreso=IngresosDeclaracion.objects.get(tipo_ingreso=1, declaraciones=declaracion)
                    neto = ingreso.ingreso_mensual_neto
                    ingreso.ingreso_mensual_pareja_dependientes=monto
                    ingreso.ingreso_mensual_total=monto+neto
                    ingreso.save()
                except Exception as e:
                    print(e)

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
                    return redirect('declaracion:dependientes-economicos',folio=folio_declaracion)

            if request.POST.get("accion") == "guardar_salir":
                return redirect('declaracion:perfil')
            if request.POST.get("accion") == "guardar_otro":
                return redirect('declaracion:dependientes-economicos-agregar',
                                folio=folio_declaracion)

            return HttpResponseRedirect(
                reverse_lazy('declaracion:ingresos-netos',
                             args=[folio_declaracion]))

        #Se obtiene la url de la sección para obtener el nombre y que este sea buscado en DB para obtener el ID
        #Esta información es utilizada para obtener la configuración de los campos(obligatorios y privados)
        current_url = resolve(request.path_info).url_name
        current_url = current_url.replace('-agregar','').replace('-editar','').replace('-borrar','')
        seccion = Secciones.objects.filter(url=current_url).first()

        


        return render(request, self.template_name, {
            'actividad_laboral_sector_form': actividad_laboral_form,
            'conyuge_dependiente_form': conyuge_dependiente_form,
            'observaciones_form': observaciones_form,
            'info_personal_var_form': info_personal_var_form,
            'domicilio_form': domicilio_form,
            'folio_declaracion': folio_declaracion,
            'informacion_registrada': informacion_registrada,
            'agregar': agregar,
            'editar_id': editar_id,
            'avance':declaracion.avance,
            'campos_privados': campos_configuracion(seccion,'p'),
            'campos_obligatorios': campos_configuracion(seccion,'o'),
        })
