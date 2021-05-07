from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.forms import PasswordInput, DateInput
from django.core import exceptions

from declaracion.models import InfoPersonalVar
from sitio.models import sitio_personalizacion
from declaracion.models.catalogos import CatPaises, CatEntidadesFederativas, CatEntesPublicos, CatPuestos, CatAreas
from bootstrap_datepicker_plus import DatePickerInput
import django.contrib.auth.password_validation as validators
import datetime


class RegistroForm(forms.Form):
    try:
        if sitio_personalizacion.objects.filter(id=1).exists():
           entidad = sitio_personalizacion.objects.first().nombre_institucion
        else:
            entidad = ""
    except Exception as e:
        entidad = ""

    nombres = forms.CharField(required = True,label="")
    apellido1 = forms.CharField(required = True,label="")
    apellido2 = forms.CharField(required = True,label="")
    telefono = forms.CharField(max_length=15,required = True,label="",validators=[RegexValidator('^\+?1?\d{9,10}$', message="Introduzca un Teléfono válido")])
    areas = forms.ModelChoiceField(queryset=CatAreas.objects.all(),required=True, label="" )
    puesto = forms.ModelChoiceField(queryset=CatPuestos.objects.all(),required=True,label="")
    rfc = forms.CharField(max_length=13, label="", required=True,validators=[RegexValidator('^([A-Z,Ñ,&]{3,4}([0-9]{2})(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])[A-Z|\d]{3})$', message="Introduzca un RFC válido")])
    YEARS= [x for x in range(1920,datetime.date.today().year+1)]
    fecha = forms.DateField(label='Fecha de ingreso', widget=forms.SelectDateWidget(years=YEARS))
    email = forms.EmailField(required=True, label="")
    contrasena1 = forms.CharField(widget=PasswordInput,required=True, label="")
    contrasena2 = forms.CharField(widget=PasswordInput,required=True, label="")

    def clean(self):
        super().clean()
        email = self.cleaned_data.get("email")
        email = str(email).lower()
        rfc = self.cleaned_data.get("rfc")
        rfc = str(rfc).upper()

        if User.objects.filter(username = rfc, is_active=True).count()>0 :
            self.add_error("email","Correo ya registrado")

        if User.objects.filter(username = rfc, is_active=True).count()>0 :
            self.add_error("rfc","RFC ya registrado")

        c1 = self.cleaned_data.get('contrasena1')
        c2 = self.cleaned_data.get('contrasena2')

        if c1 != c2:
            self.add_error('contrasena1','Contraseñas no coinciden')
        elif c1 is  None or  c1=="":
            self.add_error('contrasena1', 'Debes escribir una contraseña')
        else:
            try:
                validators.validate_password(password=c1, user=User)
            except exceptions.ValidationError as e:
                self.errors['contrasena1'] = list(e.messages)

class CambioEntePublicoForm(forms.Form):
    nombre_ente_publico = forms.CharField(required=True, label='Ente público')