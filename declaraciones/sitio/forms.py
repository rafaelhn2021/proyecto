from django import forms
from django.contrib.auth.models import User
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate, login, logout,get_user_model,password_validation
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import datetime


UserModel = get_user_model()

class PasswordResetForm(forms.Form):
    rfc = forms.CharField(label="RFC", max_length=254)

    def send_mail(self, subject_template_name, email_template_name,context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)

            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def get_users(self, username):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = UserModel._default_manager.filter(**{
            'username__iexact':  username,
            'is_active': True,
        })
        return (u for u in active_users if u.has_usable_password())

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name='registration/password_reset_email.html',
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        rfc = self.cleaned_data["rfc"]
        tt = False
        for user in self.get_users(rfc):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                user.email, html_email_template_name='registration/password_reset_email.html',
            )
            tt = True
        return tt



class LoginForm(forms.Form):

    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if User.objects.filter(username=username).count() ==0:
            self.add_error("username","RFC no registrado")
        else:
            user = User.objects.get(username=username)
            if user.is_active:
                user = authenticate(username=username, password=password)
                if not user or not user.is_active:
                    self.add_error("password", "Contraseña incorrecta")

            else:
                self.add_error("username", "Usuario inactivo, revisa tu correo y sigue las instrucciones para activar tu usuario")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user


class Personalizar_datosEntidadForm(forms.Form):
    """
        Formulario para editar los datos de la entidad 
    """
    nombre_institucion = forms.CharField(label="Nombre de la entidad", max_length=300)
    siglas_sistema = forms.CharField(label="Siglas del sistema", max_length=30)
    direccion_calle = forms.CharField(label="Calle, número y numero interior de la entidad", max_length=300)
    direccion_cp = forms.CharField(label="código postal de la entidad", max_length=300)
    direccion_ciudad = forms.CharField(label="ciudad de la entidad", max_length=300)
    direccion_estado = forms.CharField(label="estado de la entidad", max_length=300)
    direccion_telefonos = forms.CharField(label="telefono de la entidad", max_length=300)
    direccion_correos = forms.CharField(label="correos electrónico de la entidad", max_length=300)
    #activar_captcha = forms.BooleanField(label="Activar o desactivar los captcha (necesitas haber dado de alta una llave correcta en el campo 'llave para el captcha de google')",)
    google_captcha_sitekey = forms.CharField(label="Clave sitio web para el captcha de Google ", max_length=300)
    google_captcha_secretkey = forms.CharField(label="Clave secreta captcha de Google ", max_length=300,)
    terminosCondiciones_registro = forms.FileField(label="PDF con los terminos y condiciones al registrarse")
    imagen_logo = forms.ImageField(label="imagen logo")
    imagen_sublogo = forms.ImageField(label="imagen logo simplificado ")
    imagen_inicioFondo = forms.ImageField(label="imagen fondo del index")
    imagen_inicioPiepagina = forms.ImageField(label="imagen pie de página del index")
    imagen_defaultPerfil = forms.ImageField(label="imagen default para el perfil de usuario")

    def clean(self):
        super().clean()