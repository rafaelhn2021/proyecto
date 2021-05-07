from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View

from declaracion.forms import RegistroForm, CambioEntePublicoForm
from declaracion.models import InfoPersonalFija, InfoPersonalVar, Declaraciones
from declaracion.views.utils import obtiene_avance, obtiene_rfc
from sitio.util import account_activation_token
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from sitio.models import sitio_personalizacion as personalizacion, Valores_SMTP
from .mailto import mail_conf

from declaracion.models.catalogos import (CatPuestos)
from django.http import JsonResponse

import requests
import json

def listaPuestos(request):
    """
    Función que se encarga de filtar los puestos de las areas
    """
    area = request.GET.get('area')
    area_nombre = ''
    puestos = CatPuestos.objects.none()
    options = '<option value="" selected="selected">---------</option>'
    if area:
        puestos = CatPuestos.objects.filter(cat_areas=area)
        area_nombre = puestos.first().cat_areas.codigo
        options = '<option value="" nivel="" selected="selected">--------{}-----</option>'.format(area_nombre)
    for puesto in puestos:
        options += '<option value="%s" nivel="%s">%s</option>' % (
            puesto.pk,
            puesto.codigo,
            puesto.puesto
        )
    response = {}
    response['puestos'] = options
    return JsonResponse(response)


class RegistroView(View):
    """
    Class RegistroView vista basada en clases guarda los usuarios de nuevo ingreso
    """
    template_name = 'declaracion/registro.html'
    template_redirect='sitio/login.html'
    form_redirect = None
    is_staff = False
    try:
        cap_webkey =personalizacion.objects.first().google_captcha_sitekey

    except Exception as e:
        cap_webkey =''



    def get(self, request, *args, **kwargs):
        """
        Function get muestra formulario de registro y precarga algunos valores
        """
        personalizacion_data = personalizacion.objects.first()
        if request.user.is_authenticated and not self.is_staff:
            return redirect('logout')
        cap_bool = personalizacion_data.recaptcha

        context = {
            'form': RegistroForm(initial={'entidad':14}),
            'cap_webkey':self.cap_webkey,
            'cap_bool':cap_bool,
            'is_staff': self.is_staff
        }

        if personalizacion_data:
            if personalizacion_data.terminosCondiciones_registro:
                context.update({'file_terminos_condiciones': personalizacion_data.terminosCondiciones_registro})
        
        
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        """
        Function post guarda usuarios de nuego ingreso
        ---------
        Debido a que el usuario ya existirá en el modelo auth_user de Django se crearan un nuevo registro en InfoPersonalFija modelo propio del sistema
        """
        error=""
        cap_bool =personalizacion.objects.first().recaptcha

        registro = RegistroForm(request.POST)
        if registro.is_valid():
            email = registro.cleaned_data.get('email')
            rfc = registro.cleaned_data.get('rfc')
            rfc = rfc.upper()

            try:
                ente_p =personalizacion.objects.first().nombre_institucion
                cap_bool =personalizacion.objects.first().recaptcha
                cap_secret =personalizacion.objects.first().google_captcha_secretkey


            except Exception as e:
                ente_p = 'Secretaría Ejecutiva'
                cap_secret =''



            password = registro.cleaned_data.get('contrasena1')

            nombre = registro.cleaned_data.get("nombres")
            apellidos = registro.cleaned_data.get("apellido1")+" "+registro.cleaned_data.get("apellido2")
            if cap_bool:
                #captcha
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

            if valido_captcha:
                try:
                    user =  User.objects.get(username=rfc) #/AGREGADO: Se agrego para actualizar el usuario que ya estará registrado previamente
                    user.set_password(password)
                    user.save()
                    User.objects.filter(username=rfc).update(is_active=1,is_staff=self.is_staff)
                except:
                    return render(request,'declaracion/usuario-no-registrado.html',{})

                datos = InfoPersonalFija(
                    nombres=nombre,
                    apellido1=registro.cleaned_data.get("apellido1"),
                    apellido2=registro.cleaned_data.get("apellido2"),
                    rfc=rfc,
                    fecha_nacimiento = obtiene_rfc(rfc),
                    usuario=user,
                    nombre_ente_publico=ente_p,
                    fecha_inicio=registro.cleaned_data.get('fecha'),
                    telefono=registro.cleaned_data.get('telefono'),
                    puesto=registro.cleaned_data.get('puesto'),
                    cat_puestos=registro.cleaned_data.get('puesto')
                    
                )
                datos.save()

                try:
                    smtp = Valores_SMTP.objects.filter(pk=1)

                    for s in smtp:
                        mailaddress = s.mailaddress
                        mailpassword = s.mailpassword
                        nombre_smtp = s.nombre_smtp
                        puerto = s.puerto

                    send_mail=mail_conf()
                    send_mail.mail_to(email, nombre, ente_p, mailaddress, mailpassword, nombre_smtp, puerto)
                except Exception as e:
                    print (e)

                return render(request, self.template_redirect,
                                       {'form': None, 'msg': True, 
                                      'infopersonalfija': datos,
                                       'is_staff': self.is_staff,
                                       'cap_webkey':self.cap_webkey,
                                       'cap_bool':cap_bool
                                       })


        return render(request, self.template_name, {
            'form': registro,
            'error': error,
            'cap_webkey':self.cap_webkey,
            'cap_bool':cap_bool,
            'is_staff':self.is_staff

        })

class PerfilView(View):
    """
    Classs PerfilView muestra información resumida del perfil de usuario
    """
    template_name="declaracion/perfil.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        form = CambioEntePublicoForm()
        infopersonalfija = InfoPersonalFija.objects.filter(usuario=request.user).first()
        if infopersonalfija is None:
            declaracion = None
        else:
            try:
                declaracion = Declaraciones.objects.filter(info_personal_fija=infopersonalfija).filter(
                    Q(cat_estatus__isnull=True) | Q(cat_estatus__pk__in=(1, 2, 3))).first()
            except:
                pass

            try:
                declaracion.avance= obtiene_avance(declaracion)[0]
                declaracion.save()
            except Exception as e:
                print(e)

        return render(request, self.template_name, {
            'user':request.user,
            'form':form,
            'infopersonalfija':infopersonalfija,
            'declaracion':declaracion,
            'personalizacion': personalizacion.objects.all()[0]
        })



    @method_decorator(login_required(login_url='/login'))
    def post(selfself,request):
        form = CambioEntePublicoForm(request.POST)
        if form.is_valid():
            InfoPersonalFija.objects.filter(usuario=request.user).update(nombre_ente_publico=form.cleaned_data.get('nombre_ente_publico'))
            return HttpResponse(content="",status=200)
        else:
            return HttpResponse(content="Campo sin llenar",status=500)
