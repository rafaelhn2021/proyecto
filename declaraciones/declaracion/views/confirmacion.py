import sys, os
import uuid
import base64
import requests
from datetime import datetime, date 
from django.views import View
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from declaracion.models import (Declaraciones, InfoPersonalVar,
                                InfoPersonalFija, DatosCurriculares, Encargos,
                                ExperienciaLaboral, ConyugeDependientes,
                                Observaciones, SeccionDeclaracion, Secciones, IngresosDeclaracion, 
                                MueblesNoRegistrables, BienesInmuebles, ActivosBienes, BienesPersonas, 
                                BienesMuebles,SociosComerciales,Membresias, Apoyos,ClientesPrincipales,
                                BeneficiosGratuitos, Inversiones, DeudasOtros, PrestamoComodato, Fideicomisos,DeclaracionFiscal)
from declaracion.models.catalogos import CatPuestos
from declaracion.forms import ConfirmacionForm
from .utils import (validar_declaracion, campos_configuracion_todos, declaracion_datos,set_declaracion_extendida_simplificada)
from django.conf import settings
from django.forms.models import model_to_dict
from itertools import chain
from django.conf import settings    
from django.views.decorators.cache import cache_page
from sitio.models import Valores_SMTP, sitio_personalizacion
from .mailto import mail_conf
import json
import datetime
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration 




CACHE_TTL = getattr(settings, 'CACHE_TTL', 60*1)


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
    except Exception as e:
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
        if seccion:
            observaciones = seccion.observaciones
        else:
            observaciones = ''
    else:
        declaracion = {}
        info_personal_var = {}
        info_personal_fija = {}
        datos_curriculares = {}
        encargos = {}
        experiecia_laboral = {}
        conyuge_dependientes = {}

    context = {
        'declaracion': declaracion,
        'info_personal_var': info_personal_var,
        'info_personal_fija': info_personal_fija,
        'datos_curriculares': datos_curriculares,
        'encargos': encargos,
        'experiecia_laboral': experiecia_laboral,
        'conyuge_dependientes': conyuge_dependientes,
        'otros_dependientes': otros_dependientes,
        'observaciones': observaciones,
        'folio_declaracion': folio_declaracion,
        'avance':declaracion.avance
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
        pasivas = declaracion.representaciones_set.filter(es_representacion_activa=False).all()
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

    except Exception as e:
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



def get_context_pasivos(folio_declaracion, usuario):
    """
    Function get_context_pasivos
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

    except Exception as e:
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


def get_context_ingresos(folio_declaracion, usuario):
    """
    Function get_context_ingresos
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

    except Exception as e:
        IngresosNetos = {}

    context = {
        'IngresosNetos': IngresosNetos,
        'IngresosNetos_anterior':IngresosNetos_anterior
    }

    return context


def get_inmuebles(dictionary, objs, name, title=''):
    datos = []
    obj = objs[0]
    for i_, info in enumerate(obj):
        dictionary.append('<div class="col-12">')
        if i_ == 0: dictionary.append('<h6> '+title+' # '+str(i_+1)+'</h6>')
        dictionary.append(' '+name+ "<br>")
        for i, field in enumerate(model_to_dict(info)): # got only key names
            value = datos[i]
            verbose = obj.model._meta.get_field(field).verbose_name
            if verbose != 'ID':
                dictionary.append('<dl class="p_opciones col-12"><dt>')
                if value == None: value = ''
                dictionary.append(verbose +'</dt><dd class="text-black_opciones">'+ str(value)+"</dd></dl>")
        dictionary.append('</div>')
    return dictionary


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

        activos_bienes = ActivosBienes.objects.filter(declaraciones=declaracion, cat_activo_bien_id=ActivosBienes.BIENES_INMUEBLES).first() 
        Inmueble_declarante = BienesPersonas.objects.filter(activos_bienes=activos_bienes, cat_tipo_participacion_id=BienesPersonas.DECLARANTE)
        Inmuebles_propAnterior = BienesPersonas.objects.filter(activos_bienes=activos_bienes, cat_tipo_participacion_id=BienesPersonas.PROPIETARIO_ANTERIOR)
        

        kwargs = { 'folio_declaracion':folio_declaracion }
        agregar, editar_id, bienes_inmuebles_data, informacion_registrada = ( declaracion_datos(kwargs, BienesInmuebles, declaracion))
        
        #inmueble = sorted(chain(informacion_registrada, Inmueble_declarante, Inmuebles_propAnterior), key=lambda instance: instance.created_at)

        inmueble = BienesInmuebles.objects.filter(declaraciones=declaracion)
        vehiculos = MueblesNoRegistrables.objects.filter(declaraciones=declaracion)
        muebles = BienesMuebles.objects.filter(declaraciones=declaracion)
        error = {}
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
        declaracion = {}
        inmueble = {}
        vehiculos = {}
        muebles = {}
        error = e

    context.update({
        'declaracion': declaracion,
        'inmuebles': inmueble,
        'vehiculos': vehiculos,
        'muebles': muebles, 
        'error': error,
    })

    return context

#@cache_page(CACHE_TTL)
class ConfirmacionAllinOne(View):
    """
    Class ConfirmacionAllinOne vista basada en clases muestra información de todas las secciones de la declaración
    """
    template_name = "declaracion/confirmacion/all.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        """
        Function get obtiene la información de todas las secciones de declaración y la envia 
        a un template que será presentado al usuario
        """
        context = {}
        folio_declaracion = self.kwargs['folio']
        usuario = request.user

        context.update(get_context_InformacionPersonal(folio_declaracion, usuario))
        context.update(get_context_Intereses(folio_declaracion, usuario))
        context.update(get_context_ingresos(folio_declaracion, usuario))
        context.update(get_context_activos(folio_declaracion, usuario))
        context.update(get_context_pasivos(folio_declaracion, usuario))

        declaracion = Declaraciones.objects.filter(folio=uuid.UUID(folio_declaracion), info_personal_fija__usuario=usuario).all()[0]
        vehiculos = MueblesNoRegistrables.objects.filter(declaraciones=declaracion)
        inversiones = Inversiones.objects.filter(declaraciones=declaracion)
        adeudos = DeudasOtros.objects.filter(declaraciones=declaracion)
        prestamos = PrestamoComodato.objects.filter(declaraciones=declaracion,campo_default=0)
        fideicomisos = Fideicomisos.objects.filter(declaraciones=declaracion)
        context.update({"vehiculos": vehiculos})
        context.update({"inversiones": inversiones})
        context.update({"adeudos": adeudos})
        context.update({"prestamos": prestamos})
        context.update({"fideicomisos": fideicomisos})

        context.update({"fiscal": DeclaracionFiscal.objects.filter(declaraciones=declaracion.pk).first()})
        context.update({"valor_privado_texto": "VALOR PRIVADO"})

        #Determina la información a mostrar por tipo de declaración
        context.update(set_declaracion_extendida_simplificada(context['info_personal_fija']))

        return render(request, self.template_name, context)


class ConfirmarDeclaracionView(View):
    template_name = "sitio/descargar.html"
    """
    Class ConfirmarDeclaración se encarga de realiar el cierre de la declaración
    """
    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        raise Http404()

    @method_decorator(login_required(login_url='/login'))
    def post(self, request, *args, **kwargs):
        """
        Function post recibe y guarda información de la declaración
        --------
        Una vez guardad el usuario ya no podrá relizar modificaciones
        --------
        Se le solicita la usuario que indique si los campos serán públicos o no

        
        """

        usuario = request.user


        folio_declaracion = self.kwargs['folio']
        declaracion = validar_declaracion(request, folio_declaracion)
        if 'user' in request:
            usuario = request.user
        else:
            usuario = declaracion.info_personal_fija.usuario.pk
        
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
        prestamos = PrestamoComodato.objects.filter(declaraciones=declaracion, campo_default=0)
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
        
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = "inline; filename={}_{}.pdf".format(usuario_.username,declaracion.cat_tipos_declaracion)
        html = render_to_string(self.template_name, context)

        year=datetime.date.today().year
        tipo=declaracion.cat_tipos_declaracion.codigo
        if context['info_personal_fija']:
            if context['info_personal_fija'].cat_puestos:
                area = context['info_personal_fija'].cat_puestos.cat_areas.codigo
            else: 
                area=""
        else: 
            area=""
        font_config = FontConfiguration()
        directory = './media/declaraciones/'+tipo+'/'+str(year)+'/'+area+'/'
        filename = "{}_{}.pdf".format(usuario_.username,declaracion.cat_tipos_declaracion)
        file_path = os.path.join(directory, filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        pdf2 = HTML(string=html,base_url=request.build_absolute_uri()).write_pdf(font_config=font_config) #Convierte html a pdf para descargarse
        f = open(file_path, "wb")
        f.write(pdf2)
        f.close()

        try:
            confirmacion = ConfirmacionForm(request.POST)
            if confirmacion.is_valid():

                info_personal_fija = InfoPersonalFija.objects.filter(usuario=usuario).first()

                declaracion.cat_estatus_id = 4
                declaracion.fecha_recepcion = datetime.date.today()
                #declaracion.datos_publicos = bool(request.POST.get('datos_publicos'))

                if 'datos_publicos' in request.POST:
                    datos_publicos = json.loads(request.POST.get('datos_publicos').lower())
                else:
                    datos_publicos = False

                declaracion.datos_publicos = datos_publicos

                declaracion.save()
                #return redirect('declaraciones-previas')
            else:
                messages.warning(request, u"Debe indicar si los datos serán públicos")
                return redirect('declaracion:confirmar-allinone', folio=declaracion.folio)
        except Exception as e:
            print (e)
            messages.error(request, e)
            return redirect('declaracion:confirmar-allinone', folio=declaracion.folio)

        try:
            smtp = Valores_SMTP.objects.filter(pk=1)

            for s in smtp:
                mailaddress = s.mailaddress
                mailpassword = s.mailpassword
                nombre_smtp = s.nombre_smtp
                puerto = s.puerto

            send_mail=mail_conf()
            send_mail.mail_to_final(usuario_.email, info_personal_fija.nombres, info_personal_fija.apellido1, info_personal_fija.apellido2,info_personal_fija.nombre_ente_publico, declaracion.folio, declaracion.cat_tipos_declaracion.tipo_declaracion, mailaddress, mailpassword, nombre_smtp, puerto)
        except Exception as e:
            print (e)
            messages.warning(request, u"La declaracion se guardo pero no se envio el correo. Contactar a soporte para la configuracion SMPT" + str(e))

        return redirect('declaraciones-previas')