import uuid

from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms.models import model_to_dict
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail #, EmailMultiAlternatives
from .mailto import mail_conf
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib import messages

from declaracion.forms import (BusquedaDeclaranteForm, BusquedaDeclaracionForm,
                                BusquedaUsuariosForm,RegistroUsuarioOICForm,BusquedaGraficasForm,
                                RegistroUsuarioDeclaranteForm, BusquedaDeclaracionExtForm)
from declaracion.models import (Declaraciones, InfoPersonalVar,
                                InfoPersonalFija, DatosCurriculares, Encargos,
                                ExperienciaLaboral, ConyugeDependientes,
                                Observaciones, SeccionDeclaracion, Secciones, IngresosDeclaracion, 
                                MueblesNoRegistrables, BienesInmuebles, ActivosBienes, BienesPersonas, 
                                BienesMuebles,SociosComerciales,Membresias, Apoyos,ClientesPrincipales,
                                BeneficiosGratuitos, Inversiones, DeudasOtros, PrestamoComodato, Fideicomisos, DeclaracionFiscal,
                                CatTiposDeclaracion)
from declaracion.models.catalogos import CatPuestos
from declaracion.views import RegistroView
from declaracion.views.confirmacion import (get_context_InformacionPersonal,get_context_Intereses,get_context_pasivos,
                                            get_context_ingresos,get_inmuebles,get_context_activos, get_context_activos,
                                            get_context_vehiculos, get_context_inversiones, get_context_deudasotros,
                                            get_context_prestamocomodato, get_context_fideicomisos)
from .utils import set_declaracion_extendida_simplificada
from sitio.util import account_activation_token
from sitio.models import sitio_personalizacion, Valores_SMTP

from datetime import datetime, date
from rest_framework.views import APIView 
from rest_framework.response import Response

from weasyprint import HTML
from weasyprint.fonts import FontConfiguration
from django.http import HttpResponse
from django.template.loader import render_to_string


class BusquedaDeclarantesFormView(View):
    template_name="declaracion/admin/busqueda-declarantes.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self,request,*args,**kwargs):

        if request.user.is_staff:
            return render(request,self.template_name,{'form':BusquedaDeclaranteForm()})
        else:
            return redirect('login')

    @method_decorator(login_required(login_url='/login'))
    def post(self,request,*args,**kwargs):
        if request.user.is_staff:
            request_post = request.POST
            form = BusquedaDeclaranteForm(request_post)
            usuarios_sin_infopersonalfija = []
            result = None
            tipo_registro = 'registrado'

            if form.is_valid():
                result = InfoPersonalFija.objects.filter(usuario__is_staff=False, usuario__is_superuser=False)
                fin_day = int(request_post.get('fecha_fin_day')) + 1 if int(request_post.get('fecha_fin_day')) <= 27 else int(request_post.get('fecha_fin_day'))

                tipo_registro = form.cleaned_data.get('tipo_registro')
                page = form.cleaned_data.get('page')
                page_size =form.cleaned_data.get('page_size')
                nombre = form.cleaned_data.get('nombre')
                apellido1 = form.cleaned_data.get('apellido1')
                rfc = form.cleaned_data.get('rfc_search')
                fecha_inicio = date(int(request_post.get('fecha_inicio_year')),int(request_post.get('fecha_inicio_month')),int(request_post.get('fecha_inicio_day')))
                fecha_fin = date(int(request_post.get('fecha_fin_year')),int(request_post.get('fecha_fin_month')),int(request_post.get('fecha_fin_day')))
                fecha_fin_mas_uno = date(int(request_post.get('fecha_fin_year')),int(request_post.get('fecha_fin_month')), fin_day )
                estatus = form.cleaned_data.get('estatus')
                q = Q(pk__isnull=False)

                if tipo_registro == 'registrado':
                    if nombre and not nombre=="":
                        q &= Q(nombres__icontains=nombre)
                    if apellido1 and not apellido1=="":
                        q &= Q(apellido1__icontains=apellido1)
                    if rfc and not rfc=="":
                        q &= Q(rfc__icontains=rfc)
                    if estatus:
                        q &= Q(usuario__is_active = estatus)
                    if fecha_inicio and fecha_fin:
                        q &= Q(fecha_inicio__range=[fecha_inicio,fecha_fin])
                else:

                    result_usuarios = User.objects.filter(is_staff=False, is_superuser=False)

                    for usuario in result_usuarios:
                        if not InfoPersonalFija.objects.filter(usuario=usuario):
                            usuarios_sin_infopersonalfija.append(usuario.pk)

                    result = result_usuarios.filter(pk__in=usuarios_sin_infopersonalfija)

                    if nombre and not nombre=="":
                        q &= Q(first_name__icontains=nombre)
                    if apellido1 and not apellido1=="":
                        q &= Q(last_name__icontains=apellido1)
                    if rfc and not rfc=="":
                        q &= Q(username__icontains=rfc)
                    if estatus:
                        q &= Q(is_active = estatus)
                    if fecha_inicio and fecha_fin:
                        q &= Q(date_joined__range=[fecha_inicio,fecha_fin_mas_uno])

                result = result.filter(q)

                if page and page.isdigit():
                    page = int(page)
                else:
                    page=1

                if page_size and page_size.isdigit():
                    page_size = int(page_size)
                else:
                    page_size=10

                paginator = Paginator(result, page_size)
                result = paginator.get_page(page)

            parametros = {
                'form':form,
                'tipo_registro': tipo_registro
            }

            if result:
                parametros.update({'result':result})
                parametros.update({'paginas': range(1, paginator.num_pages + 1)})

            return render(request,self.template_name,parametros)
        else:
            return redirect('declaracion:index')


class BusquedaUsuariosFormView(View):
    template_name="declaracion/admin/busqueda-usuarios.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self,request,*args,**kwargs):

        if request.user.is_staff:
            return render(request,self.template_name,{'form':BusquedaUsuariosForm()})
        else:
            return redirect('login')

    @method_decorator(login_required(login_url='/login'))
    def post(self,request,*args,**kwargs):
        if request.user.is_staff:
            form = BusquedaUsuariosForm(request.POST )
            result = InfoPersonalFija.objects.filter(usuario__is_staff=True)

            if form.is_valid():
                page = form.cleaned_data.get('page')
                page_size =form.cleaned_data.get('page_size')
                nombre = form.cleaned_data.get('nombre')
                estatus = form.cleaned_data.get('estatus')
                puesto = form.cleaned_data.get('puesto_str')

                if nombre and not nombre=="":
                    result = result.filter( nombres__icontains=nombre)
                apellido1 = form.cleaned_data.get('apellido1')
                if apellido1 and not apellido1=="":
                    result = result.filter( apellido1__icontains=apellido1)
                apellido2 = form.cleaned_data.get('apellido2')
                if apellido2 and not apellido2=="":
                    result = result.filter( apellido2__icontains=apellido2)
                if estatus:
                    result = result.filter( usuario__is_active = estatus)
                rfc = form.cleaned_data.get('rfc')
                if rfc and not rfc=="":
                    result = result.filter(rfc__icontains=rfc)
                if puesto:
                    puesto_data = CatPuestos.objects.filter(puesto__contains=puesto)
                    puestos = []

                    for puesto in puesto_data:
                        puestos.append(puesto.pk)

                    result = result.filter(cat_puestos__in=puestos)

                if page and page.isdigit():
                    page = int(page)
                else:
                    page=1
                if page_size and page_size.isdigit():
                    page_size = int(page_size)
                else:
                    page_size=10

        no_results = False
        if result.count() == 0:
            no_results = True

        paginator = Paginator(result, page_size)
        result = paginator.get_page(page)

        return render(request,self.template_name,{'form':form,'result':result,'paginas': range(1, paginator.num_pages + 1), 'no_results':no_results} )


class BusquedaDeclaracionesFormView(View):
    template_name="declaracion/admin/busqueda-declaraciones.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self,request,*args,**kwargs):

        if request.user.is_staff:
            return render(request,self.template_name,{'form':BusquedaDeclaracionForm()})
        else:
            return redirect('login')

    @method_decorator(login_required(login_url='/login'))
    def post(self,request,*args,**kwargs):
        if request.user.is_staff:
            request_post = request.POST
            form = BusquedaDeclaracionForm(request_post)
            result = None

            if form.is_valid():
                try:
                    fin_day = int(request_post.get('fecha_fin_day')) + 1 if int(request_post.get('fecha_fin_day')) <= 27 else int(request_post.get('fecha_fin_day'))

                    result = Declaraciones.objects.all()
                    page = form.cleaned_data.get('page')
                    page_size =form.cleaned_data.get('page_size')
                    folio = form.cleaned_data.get('folio')

                    if folio and not folio=="":
                        result = result.filter(folio=uuid.UUID(folio))
                    tipo = form.cleaned_data.get('tipo')
                    if tipo :
                        result = result.filter(cat_tipos_declaracion=tipo)
                    estatus = form.cleaned_data.get('estatus')
                    if estatus:
                        result = result.filter(cat_estatus=estatus)
                    fecha_inicio = date(int(request_post.get('fecha_inicio_year')),int(request_post.get('fecha_inicio_month')),int(request_post.get('fecha_inicio_day')))
                    fecha_fin = date(int(request_post.get('fecha_fin_year')),int(request_post.get('fecha_fin_month')),int(request_post.get('fecha_fin_day')))
                    fecha_fin_mas_uno = date(int(request_post.get('fecha_fin_year')),int(request_post.get('fecha_fin_month')), fin_day )

                    if fecha_inicio and fecha_fin:
                        result = result.filter(fecha_declaracion__range=[fecha_inicio,fecha_fin_mas_uno])

                    if page and page.isdigit():
                        page = int(page)
                    else:
                        page=1
                    if page_size and page_size.isdigit():
                        page_size = int(page_size)
                    else:
                        page_size=10

                    paginator = Paginator(result, page_size)
                    result = paginator.get_page(page)


                except Exception as e:
                    print (e)
                    messages.warning(request, u"Para buscar por folio este debe ser la cadena completa del mismo. NO SE ENCONTRARON RESULTADOS EN EL PERIODO DE FECHAS DADAS")
                    return redirect('declaracion:busqueda-declaraciones')

            context = {
                'form':form,
                'result':result
            }

            if result:
                context.update({'paginas': range(1, paginator.num_pages + 1)})

            return render(request,self.template_name,context)
        else:
            return redirect('declaracion:index')


class BusquedaUsDecFormView(View):
    template_name="declaracion/admin/busqueda-declarante-declaraciones.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self,request,*args,**kwargs):

        if request.user.is_staff:
            return render(request,self.template_name,{'form':BusquedaDeclaracionExtForm()})
        else:
            return redirect('login')

    @method_decorator(login_required(login_url='/login'))
    def post(self,request,*args,**kwargs):
        if request.user.is_staff:
            request_post = request.POST
            form = BusquedaDeclaracionExtForm(request_post)
            dec={}
            l=[]
            if form.is_valid():

                dec_status = request_post.get('dec_status')
               
                if dec_status:
                    dec = Declaraciones.objects.filter(extemporanea=dec_status)

                    for d in dec:
                        if d.info_personal_fija_id not in l:
                            l.append(d.info_personal_fija_id)

                    result = InfoPersonalFija.objects.filter(usuario__is_staff=False, id__in=l)
                else:
                    result = InfoPersonalFija.objects.filter(usuario__is_staff=False)

                page = form.cleaned_data.get('page')
                page_size =form.cleaned_data.get('page_size')
                nombre = form.cleaned_data.get('nombre')
                estatus = form.cleaned_data.get('estatus')
              
                if nombre and not nombre=="":
                    result = result.filter( nombres__icontains=nombre)
                apellido1 = form.cleaned_data.get('apellido1')
                if apellido1 and not apellido1=="":
                    result = result.filter( apellido1__icontains=apellido1)
                apellido2 = form.cleaned_data.get('apellido2')
                if apellido2 and not apellido2=="":
                    result = result.filter( apellido2__icontains=apellido2)
                rfc = form.cleaned_data.get('rfc')
                if rfc and not rfc=="":
                    result = result.filter( rfc__icontains=rfc)
                curp = form.cleaned_data.get('curp')
                if curp and not curp=="":
                    result = result.filter(curp__icontains=curp)
                if estatus:
                    result = result.filter(usuario__is_active = estatus)

                if not dec_status:
                    for r in result:
                        l.append(r.id)

                    dec = Declaraciones.objects.filter(info_personal_fija_id__in=l)

                if page and page.isdigit():
                    page = int(page)
                else:
                    page=1
                if page_size and page_size.isdigit():
                    page_size = int(page_size)
                else:
                    page_size=10

                paginator = Paginator(result, page_size)
                result = paginator.get_page(page)


            return render(request,self.template_name,{'form':form,'result':result, 'dec_status':dec_status, 'dec':dec,'paginas': range(1, paginator.num_pages + 1)})
        else:
            return redirect('declaracion:index')


class InfoDeclarantesFormView(View):
    template_name="declaracion/admin/info-declarante.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self,request,*args,**kwargs):
        usuario = self.kwargs['pk']
        context = {
            "tipo_registro": self.kwargs['tipo_registro']
        }

        if request.user.is_staff:
            if context["tipo_registro"] == 'registrado':
                result = InfoPersonalFija.objects.get(pk=usuario)
                declaraciones = Declaraciones.objects.filter(info_personal_fija=result)

                if declaraciones:
                    context.update({"declaraciones": declaraciones})

                    cargo = Encargos.objects.filter(declaraciones=declaraciones[0].pk).first()
                    if cargo:
                        context.update({"cargo": cargo})
            else:
                result = User.objects.get(pk=usuario)

            context.update({"result": result})
            return render(request,self.template_name,context)
        else:
            return redirect('login')


class InfoUsuarioFormView(View):
    template_name="declaracion/admin/info-usuario.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self,request,*args,**kwargs):

        if request.user.is_superuser:
            result = InfoPersonalFija.objects.get(usuario__pk=self.kwargs['pk'])
            return render(request,self.template_name,{'info':result})
        else:
            return redirect('login')


class InfoDeclaracionFormView(View):
    template_name="declaracion/admin/info-declaracion.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self,request,*args,**kwargs):
        context = {}

        if request.user.is_staff:
            declaracion = Declaraciones.objects.get(pk=self.kwargs['pk'])
            folio_declaracion = str(declaracion.folio)
            context.update(get_context_InformacionPersonal(declaracion))
            context.update(get_context_Intereses(declaracion))
            context.update(get_context_ingresos(declaracion))
            context.update(get_context_activos(declaracion))

            vehiculos = MueblesNoRegistrables.objects.filter(declaraciones=declaracion)
            inversiones = Inversiones.objects.filter(declaraciones=declaracion)
            adeudos = DeudasOtros.objects.filter(declaraciones=declaracion)
            prestamos = PrestamoComodato.objects.filter(declaraciones=declaracion)
            fideicomisos = Fideicomisos.objects.filter(declaraciones=declaracion)
            context.update({"vehiculos": get_context_vehiculos(declaracion)})
            context.update({"inversiones": get_context_inversiones(declaracion)})
            context.update({"adeudos": get_context_deudasotros(declaracion)})
            context.update({"prestamos": get_context_prestamocomodato(declaracion)})
            context.update({"fideicomisos": get_context_fideicomisos(declaracion)})
            context.update({"tipo": self.kwargs['tipo']})

            #Determina la información a mostrar por tipo de declaración
            context.update(set_declaracion_extendida_simplificada(context['info_personal_fija']))

            try:
                fiscal = DeclaracionFiscal.objects.filter(declaraciones=declaracion).first()
                context.update({"fiscal": fiscal})
            except Exception as e:
                return u""

            return render(request,self.template_name,context)
        else:
            return redirect('login')


class EliminarUsuarioFormView(View):
    @method_decorator(login_required(login_url='/login'))
    def post(self,request,*args,**kwargs):

        if request.user.is_superuser:
            user = User.objects.get(pk=self.kwargs['pk'])
            user.is_active=False
            user.save()
            return HttpResponse("",status=200)
        else:
            return HttpResponse("", status=500)


class NuevoUsuariosOICFormView(View):
    template_name = 'declaracion/admin/registro_usuario_oic.html'
    template_redirect='declaracion/admin/busqueda-usuarios.html'
    form_redirect = BusquedaUsuariosForm
    is_staff = True

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated or not request.user.is_superuser :
            raise Http404()

        return render(request, self.template_name, {
            'form': RegistroUsuarioOICForm(),
            'is_staff': self.is_staff
        })

    @method_decorator(login_required(login_url='/login'))
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser :
            raise Http404()

        registro = RegistroUsuarioOICForm(request.POST)

        if registro.is_valid():
            email = registro.cleaned_data.get('email')
            rfc = registro.cleaned_data.get('rfc')
            rfc = rfc.upper()

            password = User.objects.make_random_password()

            nombre = registro.cleaned_data.get("nombres")
            rol = registro.cleaned_data.get("rol")
            apellidos = registro.cleaned_data.get("apellido1")+" "+registro.cleaned_data.get("apellido2")

            user = User.objects.create_user(username=rfc,
                                            email=email,
                                            password=password,
                                            first_name=nombre,
                                            last_name=apellidos

                                            )
            user.is_superuser = registro.cleaned_data.get("rol")
            user.is_staff = True
            user.is_superuser=rol

            user.is_active=False
            user.save()
            
            datos = InfoPersonalFija(
                nombres=nombre,
                apellido1=registro.cleaned_data.get("apellido1"),
                apellido2=registro.cleaned_data.get("apellido2"),
                rfc=rfc,
                curp=registro.cleaned_data.get("rfc"),
                usuario=user,
                nombre_ente_publico=registro.cleaned_data.get("nombre_ente_publico"),
                telefono=registro.cleaned_data.get('telefono'),
                puesto="",
                cat_puestos= CatPuestos.objects.get(pk=request.POST.get('cat_puestos'))
            )
            datos.save()

            current_site = get_current_site(request)
            mail_subject = 'Activación de cuenta'
            message = render_to_string('declaracion/admin/acc_active_email_admin.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
                'protocol': request.scheme,
                'password': password
            })
            #to_email = email
            #email = EmailMultiAlternatives(
            #            mail_subject, message, to=[to_email],from_email=settings.EMAIL_SENDER
            #)
            #email.attach_alternative(message, "text/html")
            #email.send()
            try:
                #from_email = User.objects.get(username=request.user).email  # get email from creator user
                #send_mail(
                #    subject=mail_subject,
                #    message=message,
                #    html_message=message,
                #    from_email=from_email,
                #    recipient_list=[email],
                #    fail_silently=False,
                #)
                smtp = Valores_SMTP.objects.filter(pk=1)

                for s in smtp:
                    mailaddress = s.mailaddress
                    mailpassword = s.mailpassword
                    nombre_smtp = s.nombre_smtp
                    puerto = s.puerto

                send_mail=mail_conf()
                send_mail.estandar_mail_to(mail_subject, mailaddress, email, message, mailpassword, nombre_smtp, puerto)
                email_result = "Se ha enviado un correo eléctrónico a la persona que se acaba de registrar como usuario operador del ente."
            except Exception as e:
                email_result = "No se a podido enviar un correo electrónico a la persona que se acaba de registrar "#+str(e)+")"

            if self.form_redirect:
                context = {'form':self.form_redirect(),'msg':True,'infopersonalfija':datos,'is_staff':self.is_staff, 'email_result':email_result}
                return render(request,self.template_redirect,context)
            else:
                context= {'form': None, 'msg': True, 'infopersonalfija': datos, 'is_staff': self.is_staff, 'email_result':email_result}
                return render(request, self.template_redirect,context)


        return render(request, self.template_name, {
            'form': registro,
            'is_staff':self.is_staff
        })


class RegistroDeclaranteFormView(View):
    template_name = 'declaracion/admin/registro_usuario_declarante.html'
    template_redirect='declaracion/admin/busqueda-declarantes.html'
    form_redirect = BusquedaDeclaranteForm
    is_staff = True

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        editar_id = kwargs.get("pk", False)
        tipo_registro = kwargs.get("tipo_registro")
        data_usuario = None
        form_registro = RegistroUsuarioDeclaranteForm
        model_registro = User

        if editar_id:
            if tipo_registro == 'registrado':
                data_usuario = InfoPersonalFija.objects.get(pk=editar_id)
                form_registro = RegistroUsuarioOICForm
                area, estatus, email = data_usuario.cat_puestos.cat_areas , data_usuario.usuario.is_active, data_usuario.usuario.email
            else:
                data_usuario = User.objects.get(pk=editar_id)

            data_usuario = model_to_dict(data_usuario)

            #Ya que es un formulario creado manualmewnte y no desde un model, cat_areas no pertenece al info fija,por lo que al cargar los datos al formulario
            #creado este campo no se muestra así que se le asigna una variable donde se guarda el valor del area obtenido desde el campo cat_puestos de info fija
            if tipo_registro == 'registrado':
                data_usuario["cat_areas"] = area
                data_usuario["estatus"] = estatus
                data_usuario["email"] = email


        form_declarante = form_registro(initial=data_usuario)

        if not request.user.is_authenticated or not request.user.is_superuser:
            raise Http404()

        return render(request, self.template_name,{
            'editar': editar_id,
            'form': form_declarante,
            'is_staff': self.is_staff,
            'tipo_registro': tipo_registro
        })

    @method_decorator(login_required(login_url='/login'))
    def post(self, request, *args, **kwargs):
        editar_id = kwargs.get("pk", False)
        tipo_registro = kwargs.get("tipo_registro")
        data_usuario = None
        request_post = request.POST

        if editar_id:
            if tipo_registro == 'registrado':
                fecha_inicio = date(int(request_post.get('fecha_inicio_year')),int(request_post.get('fecha_inicio_month')),int(request_post.get('fecha_inicio_day')))
                info_personal_fija_data = InfoPersonalFija.objects.get(pk=editar_id)
                info_personal_fija_data.rfc = request_post.get('rfc')
                info_personal_fija_data.nombres = request_post.get('nombres').upper()
                info_personal_fija_data.apellido1 = request_post.get('apellido1').upper()
                info_personal_fija_data.apellido2 = request_post.get('apellido2').upper()
                info_personal_fija_data.cat_puestos = CatPuestos.objects.get(pk=request_post.get('cat_puestos'))
                info_personal_fija_data.fecha_inicio = fecha_inicio
                info_personal_fija_data.save()

                data_usuario_registrado = User.objects.get(pk=info_personal_fija_data.usuario.id)
                data_usuario_registrado.is_active = request_post.get("estatus")
                data_usuario_registrado.username = request_post.get("rfc")
                data_usuario_registrado.first_name = request_post.get("nombres")
                data_usuario_registrado.last_name = request_post.get("apellido1")
                data_usuario_registrado.email = request_post.get("email")
                data_usuario_registrado.save()
            else:
                data_usuario_preregistrado = User.objects.get(pk=editar_id)
                registro = RegistroUsuarioDeclaranteForm(request_post, instance=data_usuario_preregistrado)

                if registro.is_valid():
                    registro.save()
            
            context = {
                    'form':self.form_redirect(),
                    'msg':True,
                    'is_staff':self.is_staff,
                    'editar': editar_id
                }
            return render(request,self.template_redirect,context)

        else:
            registro = RegistroUsuarioDeclaranteForm(request.POST)
            if registro.is_valid():
                datos_usuario = registro.save(commit=False)
                datos_usuario.is_staff = False
                datos_usuario.is_superuser = False
                datos_usuario.is_active = 0
                datos_usuario.save()

                context = {
                    'form':self.form_redirect(),
                    'msg':True,
                    'is_staff':self.is_staff,
                    'editar': editar_id
                }
                return render(request,self.template_redirect,context)
            
            else:
                context = {
                    'form':registro,
                    'is_staff':self.is_staff
                }
                return render(request,self.template_name,context)
                

       


class EditarUsuarioFormView(View):
    template_name = 'declaracion/admin/registro_usuario_oic.html'
    template_redirect='declaracion/admin/busqueda-usuarios.html'
    form_redirect = BusquedaUsuariosForm
    is_staff = True

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated and not self.is_staff:

            return redirect('logout')
        info = InfoPersonalFija.objects.get(usuario__pk=self.kwargs['pk'])
        initial = {
            'nombres':info.nombres,
            'apellido1':info.apellido1,
            'apellido2':info.apellido2,
            'nombre_ente_publico':info.nombre_ente_publico,
            'telefono':info.telefono,
            'rfc':info.rfc,
            'email':info.usuario.email,
            'rol':info.usuario.is_superuser,
            'estatus':info.usuario.is_active,
            'id':info.usuario_id,
        }

        if info.cat_puestos:
            initial.update({'cat_puestos': info.cat_puestos})
            initial.update({'cat_areas': info.cat_puestos.cat_areas})

        return render(request, self.template_name, {
            'form': RegistroUsuarioOICForm(initial=initial),
            'is_staff': self.is_staff,
            'editar':True,
            'info':info
        })

    @method_decorator(login_required(login_url='/login'))
    def post(self, request, *args, **kwargs):
        registro = RegistroUsuarioOICForm(request.POST)

        if registro.is_valid():

            id = registro.cleaned_data.get('id')
            user = User.objects.get(pk=id)

            email = registro.cleaned_data.get('email')
            rfc = registro.cleaned_data.get('rfc')
            rfc = rfc.upper()
            nombre = registro.cleaned_data.get("nombres")
            apellidos = registro.cleaned_data.get("apellido1")+" "+registro.cleaned_data.get("apellido2")

            user.username=rfc
            user.email=email
            user.first_name=nombre
            user.last_name=apellidos

            user.is_superuser = registro.cleaned_data.get("rol")
            user.is_staff = True

            user.is_active=registro.cleaned_data.get("estatus")

            user.save()

            datos = InfoPersonalFija.objects.get(usuario__pk=id)

            datos.nombres=registro.cleaned_data.get("nombres")
            datos.apellido1=registro.cleaned_data.get("apellido1")
            datos.apellido2=registro.cleaned_data.get("apellido2")
            datos.rfc=rfc
            datos.curp=registro.cleaned_data.get("rfc")
            datos.nombre_ente_publico=registro.cleaned_data.get("nombre_ente_publico")
            datos.telefono=registro.cleaned_data.get('telefono')
            datos.puesto=registro.cleaned_data.get('puesto')
            datos.save()

            if self.form_redirect:
                return render(request,self.template_redirect,{'form':self.form_redirect(),'msg':False,'infopersonalfija':datos,'is_staff':self.is_staff,'editar':True})
            else:
                return render(request, self.template_redirect,
                              {'form': None, 'msg': False, 'infopersonalfija': datos,
                               'is_staff': self.is_staff,'editar':True})


        return render(request, self.template_name, {
            'form': registro,
            'is_staff':self.is_staff,
            'editar':True,

        })


class DescargarReportesView(View):
    template_name="declaracion/admin/reportes_main.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        tipo_reporte = self.kwargs['tipo']
        request_get = request.GET
        form = BusquedaDeclaracionForm(request_get)

        #Fecha para mostrar las declaraciones en el periodo de tiempo introducido
        fin_day = int(request_get.get('fecha_fin_day')) + 1 if int(request_get.get('fecha_fin_day')) <= 27 else int(request_get.get('fecha_fin_day'))
        fecha_fin_mas_uno = date(int(request_get.get('fecha_fin_year')),int(request_get.get('fecha_fin_month')), fin_day )

        fecha_inicio = date(int(request_get.get('fecha_inicio_year')),int(request_get.get('fecha_inicio_month')),int(request_get.get('fecha_inicio_day')))
        fecha_fin = date(int(request_get.get('fecha_fin_year')),int(request_get.get('fecha_fin_month')),int(request_get.get('fecha_fin_day')))
        
        resumen = {
            'total_usuarios': 0,
            'activos':{
                'oic': [],
                'declarantes': [],
                'admin': []
            },
            'inactivos':{
                'oic': [],
                'declarantes': [],
                'admin': []
            },
            'iniciales':{
                'abiertas': 0,
                'cerradas': 0,
                'data': []
            },
            'modificacion':{
                'abiertas': 0,
                'cerradas': 0,
                'data': []
            },
            'conclusion':{
                'abiertas': 0,
                'cerradas': 0,
                'data': []
            },
            'abiertas':[],
            'cerradas':[],
            'usuarios_activos_d_inicial':[],
            'usuarios_activos_d_pendiente':[]
        }

        if tipo_reporte:
            usuarios = User.objects.filter(date_joined__range=[fecha_inicio,fecha_fin_mas_uno])
            declaraciones = Declaraciones.objects.extra(
                select={
                    'patrimonial': 'SELECT max FROM declaracion_secciondeclaracion WHERE  declaracion_secciondeclaracion.seccion_id = 1 AND declaracion_secciondeclaracion.declaraciones_id = declaracion_declaraciones.id',
                    'patrimonial_total': 'SELECT sum(num) FROM declaracion_secciondeclaracion WHERE  declaracion_secciondeclaracion.seccion_id between 2 and 16 AND declaracion_secciondeclaracion.declaraciones_id = declaracion_declaraciones.id',
                    'intereses': 'SELECT max FROM declaracion_secciondeclaracion WHERE  declaracion_secciondeclaracion.seccion_id = 17 AND declaracion_secciondeclaracion.declaraciones_id = declaracion_declaraciones.id',
                    'intereses_total': 'SELECT sum(num) FROM declaracion_secciondeclaracion WHERE  declaracion_secciondeclaracion.seccion_id between 18 and 24 AND declaracion_secciondeclaracion.declaraciones_id = declaracion_declaraciones.id',
                    'fiscal': 'SELECT max FROM declaracion_secciondeclaracion WHERE  declaracion_secciondeclaracion.seccion_id = 25 AND declaracion_secciondeclaracion.declaraciones_id = declaracion_declaraciones.id',
                    'fiscal_total': 'SELECT sum(num) FROM declaracion_secciondeclaracion WHERE  declaracion_secciondeclaracion.seccion_id = 26 AND declaracion_secciondeclaracion.declaraciones_id = declaracion_declaraciones.id'
                }
            )

            #Se realiza el filtro de acuerdo a los parametros recibidos
            if form.is_valid():
                folio = form.cleaned_data.get('folio')
                if folio and not folio=="":
                    declaraciones = declaraciones.filter(folio=uuid.UUID(folio))
                tipo = form.cleaned_data.get('tipo')
                if tipo :
                    declaraciones = declaraciones.filter(cat_tipos_declaracion=tipo)
                estatus = form.cleaned_data.get('estatus')
                if estatus:
                    declaraciones = declaraciones.filter(cat_estatus=estatus)
                declaraciones = declaraciones.filter(fecha_declaracion__range=[fecha_inicio,fecha_fin])

            for usuario in usuarios:
                resumen['total_usuarios'] = resumen['total_usuarios'] + 1
                if usuario.is_active == True:
                    #Separa aquellos usuarios que ya tiene una declaración y los que faltan
                    usuario_declaraciones = Declaraciones.objects.filter(info_personal_fija__usuario=usuario, cat_estatus=1, cat_tipos_declaracion=1)
                    usuario_declaraciones_terminadas = Declaraciones.objects.filter(info_personal_fija__usuario=usuario, cat_estatus=4, cat_tipos_declaracion=1)

                    if usuario_declaraciones.count() > 0:
                        resumen['usuarios_activos_d_inicial'].append(usuario)
                    if usuario_declaraciones_terminadas.count() == 0 and usuario_declaraciones.count() == 0:
                        resumen['usuarios_activos_d_pendiente'].append(usuario)
                    
                    #Separa por tipo de usuario
                    if usuario.is_staff and usuario.is_superuser == 0:
                        resumen['activos']['oic'].append(usuario)
                    if (usuario.is_staff == 0 and usuario.is_superuser) or (usuario.is_staff and usuario.is_superuser):
                        resumen['activos']['admin'].append(usuario)
                    if usuario.is_staff == 0 and usuario.is_superuser == 0:
                        resumen['activos']['declarantes'].append(usuario)
                    
                else:
                    #Separa por tipo de usuario
                    if usuario.is_staff and usuario.is_superuser == 0:
                        resumen['inactivos']['oic'].append(usuario)
                    if (usuario.is_staff == 0 and usuario.is_superuser) or (usuario.is_staff and usuario.is_superuser):
                        resumen['inactivos']['admin'].append(usuario)
                    if usuario.is_staff == 0 and usuario.is_superuser == 0:
                        resumen['inactivos']['declarantes'].append(usuario)

            for declaracion in declaraciones:
                #Declaraciones inciales por abiertas y cerradas
                if declaracion.cat_tipos_declaracion.pk == 1:
                    resumen['iniciales']['data'].append(declaracion)
                    if declaracion.cat_estatus.pk == 4:
                        resumen['iniciales']['cerradas'] = resumen['iniciales']['cerradas'] +1
                    else:
                        resumen['iniciales']['abiertas'] = resumen['iniciales']['abiertas'] +1
                
                #Declaraciones modificacion por abiertas y cerradas
                if declaracion.cat_tipos_declaracion.pk == 2:
                    resumen['modificacion']['data'].append(declaracion)
                    if declaracion.cat_estatus.pk == 4:
                        resumen['modificacion']['cerradas'] = resumen['modificacion']['cerradas'] +1
                    else:
                        resumen['modificacion']['abiertas'] = resumen['modificacion']['abiertas'] +1
                
                #Declaraciones conclusion por abiertas y cerradas
                if declaracion.cat_tipos_declaracion.pk == 3:
                    resumen['conclusion']['data'].append(declaracion)
                    if declaracion.cat_estatus.pk == 4:
                        resumen['conclusion']['cerradas'] = resumen['conclusion']['cerradas'] +1
                    else:
                        resumen['conclusion']['abiertas'] = resumen['conclusion']['abiertas'] +1

                #Separa por estatus de declaración sin tomar en cuenta el tip de declaración
                if declaracion.cat_estatus_id == 1:
                    resumen['abiertas'].append(declaracion)
                if declaracion.cat_estatus_id == 4:
                    resumen['cerradas'].append(declaracion)

            context = {
                'declaraciones': declaraciones,
                'tipo_reporte': tipo_reporte,
                'resumen': resumen
            }

            try:
                personalizacion_data = sitio_personalizacion.objects.filter(id=1)
                if personalizacion_data.exists():
                    context.update({'color_encabezado': personalizacion_data[0].color_primario})
            except Exception as e:
                print('error-----------------------', e)
            
            response = HttpResponse(content_type="application/pdf")
            response['Content-Disposition'] = "inline; filename={}_{}.pdf".format(tipo_reporte,usuario.username)
            html = render_to_string(self.template_name, context)

            font_config = FontConfiguration()
            HTML(string=html,base_url=request.build_absolute_uri()).write_pdf(response, font_config=font_config)
            return response

class DeclaracionesGraficas(View):
    template_name="declaracion/admin/reportes_graficas.html"

    @method_decorator(login_required(login_url='/login'))
    def get(self,request,*args,**kwargs):
        usuarios = User.objects.all()
        usuarios_activos = usuarios.filter(is_active=1)
        usuarios_baja = usuarios.filter(is_active=0)

        tipos_declaracion = ['Sin declaración']
        for tipo in CatTiposDeclaracion.objects.all():
            tipos_declaracion.append(tipo.codigo)

        context = {
           "total_usuario_activos":len(usuarios_activos),
           "total_usuario_baja":len(usuarios_baja),
           "tipos_declaracion":tipos_declaracion,
           "form":BusquedaGraficasForm(),
           "extra_params": date.today().year
        }

        return render(request,self.template_name,context)

    @method_decorator(login_required(login_url='/login'))
    def post(self,request,*args,**kwargs):
        return render(request,self.template_name)


class DeclaracionesGraficasData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format = None):
        declaraciones_por_usuario = {'sin_declaracion':0}
        tipos_declaracion = ['Sin declaración']
        request_get = request.GET
        fecha_inicio = date(date.today().year,1,1)
        fecha_fin = date(date.today().year,12,31)

        if request_get.get('year') is not None:
            fecha_inicio = date(int(request_get.get('year')),1,1)
            fecha_fin = date(int(request_get.get('year')),12,31)


        #Información que mostrará el promedio de las declaraciones creadas por la cantidad de usuario existentes
        for tipo in CatTiposDeclaracion.objects.all():
            tipos_declaracion.append(tipo.codigo)
            declaraciones_por_usuario.update({tipo.codigo: 0})

        usuarios = User.objects.all()
        usuarios_activos = usuarios.filter(is_active=1,date_joined__range=[fecha_inicio,fecha_fin], is_staff=0)
        usuarios_baja = usuarios.filter(is_active=0,date_joined__range=[fecha_inicio,fecha_fin], is_staff=0)

        declaraciones = Declaraciones.objects.all()
        declaraciones_por_anio = declaraciones.filter(fecha_declaracion__range=[fecha_inicio,fecha_fin])

        for usuario in usuarios_activos:
            usuario_declaraciones = declaraciones_por_anio.filter(info_personal_fija__usuario=usuario)
            if usuario_declaraciones.exists():
               for usu_dec in usuario_declaraciones:
                  declaraciones_por_usuario[usu_dec.cat_tipos_declaracion.codigo]+=1
            else:
                declaraciones_por_usuario['sin_declaracion']+=1

        chartdata = declaraciones_por_usuario.values()

        #Información que mostrara la cantidad de usuarios y declaraciónes creados por año
        meses = ['Enero', 'Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        if len(usuarios_activos) > len(declaraciones):
            total_usuarios_declaraciones = len(usuarios_activos)
        else:
            total_usuarios_declaraciones = len(declaraciones)

        usuarios_por_anio = usuarios.filter(date_joined__range=[fecha_inicio,fecha_fin])
        declaraciones_por_mes={}
        usuarios_por_mes={}

        for mes in meses:
            mes_index = meses.index(mes)+1
            declaraciones_mes = declaraciones_por_anio.filter(fecha_declaracion__month=mes_index)
            if declaraciones_mes:
                declaraciones_por_mes.update({mes: len(declaraciones_mes)})
            else:
                declaraciones_por_mes.update({mes:0})

            usuarios_mes = usuarios_por_anio.filter(date_joined__month=mes_index)
            if usuarios_mes:
               usuarios_por_mes.update({mes:len(usuarios_mes)})
            else:
               usuarios_por_mes.update({mes:0})

        data = {
            "labels":tipos_declaracion,
            "lables_meses": meses,
            "chartLabel":"Declaraciones",
            "chartLabel_usuario":"Usuarios",
            "chartdata":chartdata,
            "total_usuario_activos": len(usuarios_activos),
            "total_usuario_baja": len(usuarios_baja),
            "total_usuarios_declaraciones": total_usuarios_declaraciones,
            "chartdata_datos_anuales_declaraciones": declaraciones_por_mes.values(),
            "chartdata_datos_anuales_usuarios": usuarios_por_mes.values(),
            "extra_params": [request_get.get('anio')]
        }
        return Response(data)