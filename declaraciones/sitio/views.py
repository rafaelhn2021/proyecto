# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import os
import uuid, re
from itertools import chain
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration  
from django.views import View
from django.contrib import messages
#!/usr/bin/python
# -*- coding: latin-1 -*-
# -*- coding: utf-8 -*-
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic import (FormView, RedirectView, TemplateView, ListView)
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.urls import reverse_lazy, reverse, resolve
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from sitio.forms import LoginForm, PasswordResetForm
from sitio.util import account_activation_token
from declaracion.views.utils import campos_configuracion_todos,declaracion_datos,set_declaracion_extendida_simplificada
from declaracion.forms import ConfirmacionForm
from django.template.loader import render_to_string
from declaracion.models import (Declaraciones, InfoPersonalVar,
                                InfoPersonalFija, DatosCurriculares, Encargos,
                                ExperienciaLaboral, ConyugeDependientes,
                                Observaciones, SeccionDeclaracion, Secciones, IngresosDeclaracion, 
                                MueblesNoRegistrables, BienesInmuebles, ActivosBienes, BienesPersonas, 
                                BienesMuebles,SociosComerciales,Membresias, Apoyos,ClientesPrincipales,
                                BeneficiosGratuitos, Inversiones, DeudasOtros, PrestamoComodato, DeclaracionFiscal,
                                Fideicomisos)
from declaracion.models.catalogos import CatPuestos, CatAreas
from .models import declaracion_faqs as faqs, sitio_personalizacion 
from .forms import Personalizar_datosEntidadForm
import datetime
import requests
import json
from django.contrib.auth.models import User
from django.core.cache import cache
import base64


class IndexView(View):
    template_name = "sitio/index.html"
    context = {}
    
    def get(self, request):
        return render(request, self.template_name, self.context)


class FAQView(View):
    template_name = "sitio/faqs.html"
    context = {}

    def get(self, request):
        queryset = faqs.objects.all().order_by("orden").exclude(orden=0)
        self.context.update({'questions': queryset})
        return render(request, self.template_name, self.context)


class PersonalizacionDatosEntidadView(View):
    """
     ------------------------------------------------------------
        Clase para modificar los datos de la entidad del sistema sin el uso del admin
    """

    template_name = "sitio/personalizar/datosentidad.html"
    context = {}

    @method_decorator(login_required(login_url='/login'))
    def get(self, request):
        if request.user.is_superuser:
            try:
                datos = sitio_personalizacion.objects.all().first()
                form = Personalizar_datosEntidadForm(request)
            except Exception as e:
                datos = None
                form = None
            
            self.context["datos"] = datos
            self.context["form"] = form
            return render(request, self.template_name, self.context)
        else:
            return redirect('index')

    @method_decorator(login_required(login_url='/login'))
    def pos(self, request):
        if request.user.is_superuser:
            try:
                datos = sitio_personalizacion.objects.all().first()
                form = Personalizar_datosEntidadForm(request)
            except Exception as e:
                datos = None
                form = None
            self.context["datos"] = datos
            self.context["form"] = form
            return render(request, self.template_name, self.context)
        else:
            return redirect('index')
    

class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = "sitio/login.html"
    success_url =  reverse_lazy("declaracion:perfil")
    context = {}
    try:
        cap_webkey =sitio_personalizacion.objects.first().google_captcha_sitekey

    except Exception as e:
        cap_webkey =''



    def get(self, request, *args, **kwargs):
        cap_bool =sitio_personalizacion.objects.first().recaptcha

        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            context = {'form': LoginForm(), 'cap_webkey':self.cap_webkey, 'cap_bool':cap_bool}
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            if user.password == '':
                url = reverse('password_reset')
                return HttpResponseRedirect(url + "?rfc=%s" % (username))
        except:
            pass
        form = LoginForm(request.POST)
    
        try:
            ente_p =sitio_personalizacion.objects.first().nombre_institucion
            cap_secret =sitio_personalizacion.objects.first().google_captcha_secretkey
            cap_bool =sitio_personalizacion.objects.first().recaptcha
        except Exception as e:
            ente_p = 'Secretaría Ejecutiva'
            cap_secret =''
            
        if cap_bool:
            captcha_token=request.POST.get("g-recaptcha-response")
            cap_url="https://www.google.com/recaptcha/api/siteverify"
            cap_data={"secret":cap_secret,"response":captcha_token}
            cap_server_response=requests.post(url=cap_url,data=cap_data)
            cap_json=json.loads(cap_server_response.text)

            if cap_json["success"]==True:
                valido_captcha = True
            else:
                error="Llenar recaptcha, por favor"
                valido_captcha = False
        else:
            valido_captcha = True
        
        num=cache.get_or_set('intentos',0,300)
       
        if num<5:
            if valido_captcha:
                
                if form.is_valid():
                    login(request,user, backend='django.contrib.auth.backends.ModelBackend')
                    return HttpResponseRedirect(self.get_success_url())
                else:
                    context = {'form': form,'cap_webkey':self.cap_webkey,
                'cap_bool':cap_bool}

                    num=cache.get('intentos')
                    if num:
                        num=num+1
                        cache.set('intentos',num,300)
                    else:
                        cache.set('intentos',1,300)

                    return render(request,self.template_name, context)

                return super(LoginView, self).post(request, *args, **kwargs)
            else:
                context = {'form': form,'cap_webkey':self.cap_webkey,
                'cap_bool':cap_bool, 'error':error}
                return render(request,self.template_name, context)
        else:
            error="Exceso de intentos, intente más tarde."
            context = {'form': form,'cap_webkey':self.cap_webkey,
            'cap_bool':cap_bool, 'error':error}
            return render(request,self.template_name, context)  


    def form_valid(self, form):
        login(self.request, form.get_user(), backend='django.contrib.auth.backends.ModelBackend')
        return super(LoginView, self).form_valid(form)

class LogoutView(RedirectView):
    pattern_name = 'login'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


def get_context_pasivos(folio_declaracion, usuario):
    """
    Function get_context_Intereses
    ----------
    Se obtiene información de subsecciones

    Parameters
    ----------
    folio_declaracion: str
        Cadena de texto correspondiente al folio de la declaración
    usuario: queryset
        Información del usuario logeado


    Return
    ------
    context: dict

    """
    try:
        declaracion = Declaraciones.objects.filter(folio=uuid.UUID(folio_declaracion),info_personal_fija__usuario=usuario).all()[0]
        seccion_id = Secciones.objects.filter(url='pasivos-observaciones').first()
        seccion = SeccionDeclaracion.objects.filter(declaraciones=declaracion, seccion=seccion_id).first()
        
        if seccion:
            observaciones = seccion.observaciones
        else:
            observaciones = ''

    except Exception:
        folio_declaracion = ''
        declaracion = {}

    confirmacion = ConfirmacionForm()

    context = {
        'declaracion': declaracion,
        'folio_declaracion': folio_declaracion,
        'observaciones': observaciones,
        'confirmacion': confirmacion,
        'avance':declaracion.avance
    }

    return context


def get_context_InformacionPersonal(folio_declaracion, usuario):
    """
    Function get_context_InformacionPersonal
    ----------
    Se obtiene información de subsecciones

    Parameters
    ----------
    folio_declaracion: str
        Cadena de texto correspondiente al folio de la declaración
    usuario: queryset
        Información del usuario logeado


    Return
    ------
    context: dict

    """
    try:
        declaracion = Declaraciones.objects.filter(folio=uuid.UUID(folio_declaracion), info_personal_fija__usuario=usuario).all()[0]
    except Exception:
        folio_declaracion = None

    if folio_declaracion:
        
        info_personal_var = InfoPersonalVar.objects.filter(declaraciones=declaracion).first()
        info_personal_fija = InfoPersonalFija.objects.filter(declaraciones=declaracion).first()
        datos_curriculares = DatosCurriculares.objects.filter(declaraciones=declaracion)
        encargos = Encargos.objects.filter(declaraciones=declaracion).first()
        experiecia_laboral = ExperienciaLaboral.objects.filter(declaraciones=declaracion)
        conyuge_dependientes = ConyugeDependientes.objects.filter(declaraciones=declaracion, es_pareja=True).first()
        otros_dependientes = ConyugeDependientes.objects.filter(declaraciones=declaracion, es_pareja=False)
        seccion_id = Secciones.objects.filter(url='informacion-personal-observaciones').first()
        seccion = SeccionDeclaracion.objects.filter(declaraciones=declaracion, seccion=seccion_id).first()

        dependientes_menores_edad = []
        for position,dependiente in enumerate(otros_dependientes):

            if dependiente.dependiente_infopersonalvar:
                try:
                    anio_nacimiento_dependiente = int(dependiente.dependiente_infopersonalvar.fecha_nacimiento.year)
                    anio_actual = int(date.today().year)

                    edad_dependiente = anio_actual-anio_actual

                    if edad_dependiente < 18:
                        dependientes_menores_edad.append(dependiente.pk)
                except Exception as e:
                    print('sitio/view -> Calculo de edad', e)
                    pass

        if seccion:
            observaciones = seccion.observaciones
        else:
            observaciones = ''
    else:
        info_personal_var = {}
        info_personal_fija = {}
        datos_curriculares = {}
        encargos = {}
        experiecia_laboral = {}
        conyuge_dependientes = {}
        otros_dependientes = {}
        observaciones = {}

    context = {
        'declaracion': declaracion,
        'info_personal_var': info_personal_var,
        'info_personal_fija': info_personal_fija,
        'datos_curriculares': datos_curriculares,
        'encargos': encargos,
        'experiecia_laboral': experiecia_laboral,
        'conyuge_dependientes': conyuge_dependientes,
        'otros_dependientes': otros_dependientes,
        'otros_dependientes_menores_edad': dependientes_menores_edad,
        'observaciones': observaciones,
        'folio_declaracion': folio_declaracion,
        'avance':declaracion.avance
    }

    return context


def get_context_ingresos(folio_declaracion, usuario):
    """
    Function get_context_Intereses
    ----------
    Se obtiene información de subsecciones

    Parameters
    ----------
    folio_declaracion: str
        Cadena de texto correspondiente al folio de la declaración
    usuario: queryset
        Información del usuario logeado


    Return
    ------
    context: dict

    """
    try:
        declaracion = Declaraciones.objects.filter(folio=uuid.UUID(folio_declaracion),info_personal_fija__usuario=usuario).all()[0]
        IngresosNetos = IngresosDeclaracion.objects.filter(tipo_ingreso=1, declaraciones=declaracion).first()
        IngresosNetos_anterior = IngresosDeclaracion.objects.filter(tipo_ingreso=0, declaraciones=declaracion).first()

    except Exception:
        IngresosNetos = {}

    context = {
        'IngresosNetos': IngresosNetos,
        'IngresosNetos_anterior':IngresosNetos_anterior
    }

    return context


def get_context_Intereses(folio_declaracion, usuario):
    """
    Function get_context_Intereses
    ----------
    Se obtiene información de subsecciones

    Parameters
    ----------
    folio_declaracion: str
        Cadena de texto correspondiente al folio de la declaración
    usuario: queryset
        Información del usuario logeado


    Return
    ------
    context: dict

    """
    try:
        declaracion = Declaraciones.objects.filter(folio=uuid.UUID(folio_declaracion),info_personal_fija__usuario=usuario).all()[0]
        activas = declaracion.representaciones_set.filter(es_representacion_activa=True).all()
        #pasivas = declaracion.representaciones_set.filter(es_representacion_activa=False).all()
        socio = SociosComerciales.objects.filter(declaraciones=declaracion) # old_v = False
        membresia = Membresias.objects.filter(declaraciones=declaracion) # old_v = False
        apoyo = Apoyos.objects.filter(declaraciones=declaracion) # old_v = False
        clientes = ClientesPrincipales.objects.filter(declaraciones=declaracion)
        beneficios = BeneficiosGratuitos.objects.filter(declaraciones=declaracion)

        seccion_id = Secciones.objects.filter(url='intereses-observaciones').first()
        seccion = SeccionDeclaracion.objects.filter(declaraciones=declaracion, seccion=seccion_id).first()
        if seccion:
            observaciones = seccion.observaciones
        else:
            observaciones = ''

    except Exception:
        folio_declaracion = ''
        declaracion = {}

    context = {
        'declaracion': declaracion,
        'activas': activas,
        'clientes': clientes,
        'beneficios': beneficios,
        'socios': socio,
        'membresias': membresia,
        'apoyos': apoyo,
        'folio_declaracion': folio_declaracion,
        'avance':declaracion.avance,
        'observaciones': observaciones,
    }

    return context

def get_context_activos(folio_declaracion, usuario):
    """
    Function get_context_activos
    ----------
    Se obtiene información de subsecciones

    Parameters
    ----------
    folio_declaracion: str
        Cadena de texto correspondiente al folio de la declaración
    usuario: queryset
        Información del usuario logeado


    Return
    ------
    context: dict

    """
    context = {}
    try:
        declaracion = Declaraciones.objects.filter(folio=uuid.UUID(folio_declaracion), info_personal_fija__usuario=usuario).all()[0]

        activos_bienes = ActivosBienes.objects.filter(declaraciones=declaracion, cat_activo_bien_id=ActivosBienes.BIENES_INMUEBLES).first() # toma todos los bienes inmuebles de esa declaracion
        Inmueble_declarante = BienesPersonas.objects.filter(activos_bienes=activos_bienes, cat_tipo_participacion_id=BienesPersonas.DECLARANTE)
        Inmuebles_propAnterior = BienesPersonas.objects.filter(activos_bienes=activos_bienes, cat_tipo_participacion_id=BienesPersonas.PROPIETARIO_ANTERIOR)
        

        kwargs = { 'folio_declaracion':folio_declaracion }
        agregar, editar_id, bienes_inmuebles_data, informacion_registrada = ( declaracion_datos(kwargs, BienesInmuebles, declaracion))
        
        inmueble = sorted(chain(informacion_registrada, Inmueble_declarante, Inmuebles_propAnterior), key=lambda instance: instance.created_at)
        vehiculos = MueblesNoRegistrables.objects.filter(declaraciones=declaracion)
        muebles = BienesMuebles.objects.filter(declaraciones=declaracion)
        fideicomisos = Fideicomisos.objects.filter(declaraciones=declaracion)
        error = {}
    
    except Exception as e:
        #exc_type, exc_obj, exc_tb = sys.exc_info()
        #fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e)
        declaracion = {}
        inmueble = {}
        vehiculos = {}
        muebles = {}
        fideicomisos = {}
        error = e

    context.update({
        'declaracion': declaracion,
        'inmuebles': inmueble,
        'vehiculos': vehiculos,
        'muebles': muebles,
        'fideicomisos': fideicomisos,
        'error': error,
    })

    return context


def activar(request, uidb64, token):
    """
    Function activar se encarga de activar al usuario en respuesta a la confirmación de su correo
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, '¡Tu cuenta a sido activada. ¡Cambia tu contraseña!')
        return redirect('cambiar')
    else:
        return HttpResponse('¡El enlace es invalido!')

class DeclaracionesPreviasView(ListView):
    template_name = "sitio/declaraciones-previas.html"
    context_object_name = "declaraciones"

    def get_queryset(self):
        queryset = Declaraciones.objects.filter(
            cat_estatus_id = 4,
            info_personal_fija__usuario=self.request.user
            )
        return queryset

class DeclaracionesPreviasDescargarView(View):
    template_name = "sitio/descargar.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        usuario = request.user

        try:
            folio_declaracion = self.kwargs['folio']
            declaracion = Declaraciones.objects.filter(folio=uuid.UUID(folio_declaracion)).first()
            if 'user' in request:
                usuario = request.user
            else:
                usuario = declaracion.info_personal_fija.usuario.pk
        except Exception :
            folio_declaracion = None

        context = {}

        context.update(get_context_InformacionPersonal(folio_declaracion, usuario))
        context.update(get_context_Intereses(folio_declaracion, usuario))
        context.update(get_context_ingresos(folio_declaracion, usuario))
        context.update(get_context_activos(folio_declaracion, usuario))
        context.update(get_context_pasivos(folio_declaracion, usuario))

        declaracion = Declaraciones.objects.filter(folio=uuid.UUID(folio_declaracion), info_personal_fija__usuario=usuario).all()[0]
        vehiculos = MueblesNoRegistrables.objects.filter(declaraciones=declaracion)
        inversiones = Inversiones.objects.filter(declaraciones=declaracion)
        adeudos = DeudasOtros.objects.filter(declaraciones=declaracion)
        prestamos = PrestamoComodato.objects.filter(declaraciones=declaracion, campo_default=False)
        fiscal = DeclaracionFiscal.objects.filter(declaraciones=declaracion).first()
        context.update({"vehiculos": vehiculos})
        context.update({"inversiones": inversiones})
        context.update({"adeudos": adeudos})
        context.update({"prestamos": prestamos})
        context.update({"fiscal": fiscal})
        context.update({"valor_privado_texto": "VALOR PRIVADO"})
        
        if declaracion.datos_publicos == False:
           context.update({"campos_privados": campos_configuracion_todos('p')})

        #Determina la información a mostrar por tipo de declaración
        context.update(set_declaracion_extendida_simplificada(context['info_personal_fija']))

        usuario_ = User.objects.get(pk=usuario)

        #Genera el archivo PDF
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = "inline; filename={}_{}.pdf".format(usuario_.username,declaracion.cat_tipos_declaracion)
        html = render_to_string(self.template_name, context)

        font_config = FontConfiguration()
        HTML(string=html,base_url=request.build_absolute_uri()).write_pdf(response, font_config=font_config)

        return response


class DeclaracionesPreviasVerView(View):
    template_name = "sitio/ver_declaracion.html"
    
    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        folio_declaracion = self.kwargs['folio']
        context = {
            'folio_declaracion': folio_declaracion
        }
        declaracion = Declaraciones.objects.get(folio=uuid.UUID(folio_declaracion))

        context.update(get_context_InformacionPersonal(folio_declaracion, declaracion.info_personal_fija.usuario.id))
        context.update(get_context_Intereses(folio_declaracion, declaracion.info_personal_fija.usuario.id))
        context.update(get_context_ingresos(folio_declaracion, declaracion.info_personal_fija.usuario.id))
        context.update(get_context_activos(folio_declaracion, declaracion.info_personal_fija.usuario.id))
        context.update(get_context_pasivos(folio_declaracion, declaracion.info_personal_fija.usuario.id))

        vehiculos = MueblesNoRegistrables.objects.filter(declaraciones=declaracion)
        inversiones = Inversiones.objects.filter(declaraciones=declaracion)
        adeudos = DeudasOtros.objects.filter(declaraciones=declaracion)
        prestamos = PrestamoComodato.objects.filter(declaraciones=declaracion)
        fideicomisos = Fideicomisos.objects.filter(declaraciones=declaracion)
        context.update({"vehiculos": vehiculos})
        context.update({"inversiones": inversiones})
        context.update({"adeudos": adeudos})
        context.update({"prestamos": prestamos})
        context.update({"fideicomisos": fideicomisos})

        #Determina la información a mostrar por tipo de declaración
        context.update(set_declaracion_extendida_simplificada(context['info_personal_fija']))

        return render(request, self.template_name, context)

class CambioPasswordView(View):
    template_name = 'sitio/cambio-password.html'

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user)

        return render(request, self.template_name, {
            'form': form
        })

    @method_decorator(login_required(login_url='/login'))
    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            if request.user.check_password(form.cleaned_data['new_password2']):
                messages.error(request,"Tu nueva contraseña es idéntica a la actual")
                return render(request, self.template_name, {
                    'form': form
                })

            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, '¡Tu contraseña a sido cambiada!')

            return redirect('declaracion:perfil')

        return render(request, self.template_name, {
                'form': form
        })

class PasswordResetRFCView(PasswordResetView):
    from_email=settings.EMAIL_SENDER
    form_class = PasswordResetForm
    def get(self,request,*args,**kwargs):
        rfc = request.GET.get('rfc')

        try:
            obj = User.objects.get(username=rfc,password='')
            form = PasswordResetForm(initial={'rfc':obj.username})
            return render(request,self.template_name,{'form':form})
        except Exception: # as e:
            return render(request, self.template_name, {'form': PasswordResetForm()})

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }
        if form.save(**opts):
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponse(content="",status=500)


class PersonalizacionCatalogoPuestosView(View):
    """
        ------------------------------------------------------------
        Clase para editar, crear, borrar los puestos usados en el sistema
    """
    template_name = "sitio/personalizar/catpuestos.html"
    context = {}

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, pkid=None):
        if request.user.is_superuser or request.user.is_staff:
            current_url = resolve(request.path_info).url_name
            if ("_editar" in current_url or "_eliminar" in current_url or "_agregar" in current_url) and current_url != None: 
                return redirect("peronalizar_catpuestos")

            self.context["puestos"] = CatPuestos.objects.all()
            self.context["areas"] = CatAreas.objects.all()
            return render(request, self.template_name, self.context)
        else:
            return redirect("index")
    
    # ToDo agregar multiples puestos a la vez mediante json
    @method_decorator(login_required(login_url='/login')) 
    def post(self, request, pkid=None):
        if request.user.is_staff:
            current_url = resolve(request.path_info).url_name
            
            if "_editar" in current_url and current_url != None: 

                puesto = request.POST.get("nuevo_puesto")
                codigo = request.POST.get("nuevo_puesto_codigo")
                area = request.POST.get("nueva_area")
                result = self.editar(pkid, puesto, codigo, area)

                if result != True:
                    self.context["messages"] = {result}
                else:
                    return JsonResponse({"messages": "editado"})

            if "_eliminar" in current_url and current_url != None: 
                value = ""
                result = self.eliminar(pkid)

                if result != True:
                    self.context["messages"] = {result}
                else:
                    return JsonResponse({"messages": "eliminado"})

            if "_agregar" in current_url and current_url != None:
                value = request.POST.get("input-puesto-agregar")
                codigo = request.POST.get("input-puesto_codigo-agregar")
                area_valuea = request.POST.get("input-puesto_area-agregar")
                value = value.strip()
                value_empty = re.sub(r'[^\w]', '', value)

                if value_empty == "" or value_empty is None:
                    self.context["messages"] = {"EL puesto no puede ser nulo y solo debe contener letras"}
                else:
                    result = self.agregar(value, codigo, area_valuea)
                    if result != True:
                        self.context["messages"] = {result}
                    else:
                        return JsonResponse({"message": "agregado"})

            queryset = CatPuestos.objects.all()
            self.context["puestos"] = queryset
            return render(request, self.template_name, self.context)
        else:
            return redirect("index")
    
    def editar(self, id, puesto_txt, codigo, area):
        try:
            obj = CatPuestos.objects.get(pk=id)
            obj.puesto=puesto_txt
            obj.codigo=codigo
            obj.cat_areas=CatAreas.objects.get(pk=area)
            obj.save()
        except Exception as e:
            return e
        return True

    def eliminar(self, id):
        try:
            obj = CatPuestos.objects.get(pk=id)
            obj.delete()
        except Exception as e:
            return str(e) + " " + str(id)
        return True
    
    def agregar(self, value, codigo, area):
        try:
            area = CatAreas.objects.get(pk=area)
            obj = CatPuestos(puesto=value, cat_areas=area,codigo=codigo)
            obj.save()
        except Exception as e:
            if not area:
                return 'falta área de asignacion del puesto'
                
            return 'No se puedo agregar el puesto, validar datos'
        return True

class PersonalizacionCatalogoAreasView(View):
    template_name = "sitio/personalizar/catareas.html"
    context = {}

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, pkid=None):
        if request.user.is_superuser or request.user.is_staff:
            current_url = resolve(request.path_info).url_name
            if ("_editar" in current_url or "_eliminar" in current_url or "_agregar" in current_url) and current_url != None: 
                return redirect("peronalizar_catareas")

            self.context["areas"] = CatAreas.objects.all()
            return render(request, self.template_name, self.context)
        else:
            return redirect("index")
    
    @method_decorator(login_required(login_url='/login')) 
    def post(self, request, pkid=None):
        if request.user.is_staff:
            current_url = resolve(request.path_info).url_name
            if "_editar" in current_url and current_url != None: 

                area = request.POST.get("nueva_area")
                codigo = request.POST.get("nueva_area_codigo")
                result = self.editar(pkid,area,codigo)
                
                if result != True:
                    self.context["messages"] = {result}
                else:
                    return JsonResponse({"messages": "editado"})
            if "_eliminar" in current_url and current_url != None: 
                value = ""
                result = self.eliminar(pkid)
                if result != True:
                    self.context["messages"] = {result}
                else:
                    return JsonResponse({"messages": "eliminado"})

            if "_agregar" in current_url and current_url != None:
                value_area = request.POST.get("input-area-agregar")
                value_codigo = request.POST.get("input-area-codigo-agregar")
                value = value_area.strip()
                value = re.sub(r'[^\w]', '', value)
                if value == "" or value is None:
                    self.context["messages"] = {"El área no puede ser nulo y solo debe contener letras"}
                else:
                    result = self.agregar(value_area,value_codigo)
                    if result != True:
                        self.context["messages"] = {result}
                    else:
                        return JsonResponse({"message": "agregado"})

            queryset = CatAreas.objects.all()
            self.context["areas"] = queryset
            return render(request, self.template_name, self.context)
        else:
            return redirect("index")
    
    def editar(self, id, area_txt, codigo):
        try:
            obj = CatAreas.objects.get(pk=id)
            obj.area=area_txt if area_txt else ''
            obj.codigo = codigo if codigo else ''
            obj.save()
        except Exception as e:
            return e
        return True

    def eliminar(self, id):
        try:
            obj = CatAreas.objects.get(pk=id)
            obj.delete()
        except Exception as e:
            return str(e) + " " + str(id)
        return True
    
    def agregar(self, value_area, value_codigo):
        try:
            obj = CatAreas(area=value_area,codigo=value_codigo)
            obj.save()
        except Exception as e:
            return 'No se puedo agregar el área, validar datos'
        return True

def GenerarHTMLView(request):
    template_name='sitio/generar_html.html'

    declaracionInicial = Declaraciones.objects.filter(cat_estatus_id=4, cat_tipos_declaracion_id=1).all()
    declaracionMod = Declaraciones.objects.filter(cat_estatus_id=4, cat_tipos_declaracion_id=2).all()
    areas = CatAreas.objects.all()

    context = {
    'declaracionInicial':declaracionInicial,
    'declaracionMod':declaracionMod,
    'areas':areas
    }

    html=render_to_string(template_name, context)

    archivo=open("prueba.html","w")
    archivo.write(html)
    archivo.close()


    
    return render(request, template_name, context)



def GenerarHTMLView2(request):
    template_name='sitio/generar_html.html'

    html="<html><head></head><body>"

    declaracion = Declaraciones.objects.filter(cat_estatus_id=4).all()

    for dec in declaracion:
        html=html+'<br><a target="blank" href="/media/declaraciones/'+dec.cat_tipos_declaracion.codigo+'/'+str(dec.fecha_recepcion.year)+'/'+dec.info_personal_fija.cat_puestos.cat_areas.codigo+'/'+dec.info_personal_fija.rfc +'_'+str(dec.cat_tipos_declaracion)+'.pdf" >'+ dec.info_personal_fija.rfc +'_'+str(dec.cat_tipos_declaracion)+'.pdf</a>'

    html = html+"</body></html>"
    archivo=open("/templates/sitio/generar_html.html","r")
    archivo.write(html)
    archivo.close()
        
    context = {
    'html':html
    }
    
    return render(request, template_name, context)
