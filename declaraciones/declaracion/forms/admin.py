from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from declaracion.models import CatTiposDeclaracion, InfoPersonalVar, InfoPersonalFija
from declaracion.models.catalogos import CatEntesPublicos, CatEstatusDeclaracion, CatAreas, CatPuestos

import datetime

YEARS= [x for x in range(1920,datetime.date.today().year+1)]
TRUE_FALSE_CHOICES = (
        (None,'--------'),
        (1, 'Activo'),
        (0, 'Inactivo')
    )

class BusquedaDeclaranteForm(forms.Form):

    USUARIO_REGISTRADO = [
        ('registrado', 'Registrado en el sistema'),
        ('no_registrado', 'Pre-registrado en el sistema')
    ]
    nombre = forms.CharField(max_length=128,label="Nombre", required=False )
    apellido1 = forms.CharField(max_length=128,label="Primer Apellido", required=False )
    rfc = forms.CharField(max_length=13,label="RFC", required=False,validators=[RegexValidator('^([A-Z,Ñ,&]{3,4}([0-9]{2})(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])[A-Z|\d]{3})$', message="Introduzca un RFC válido")] )
    rfc_search = forms.CharField(max_length=13,label="RFC",required=False)
    tipo_registro = forms.ChoiceField(choices=USUARIO_REGISTRADO, widget=forms.RadioSelect,label="Tipo registro",required=False, initial='registrado')
    ente = forms.ModelChoiceField(queryset=CatEntesPublicos.objects.all(),required=False,label="Ente público")
    estatus = forms.ChoiceField(choices = TRUE_FALSE_CHOICES, label="Estatus",
                              initial='', widget=forms.Select(), required=False)
    page = forms.CharField(widget=forms.HiddenInput(), required=False)
    page_size = forms.CharField(widget=forms.HiddenInput(), required=False,initial="10" )
    
    fecha_inicio = forms.DateField(label='Fecha inicial', widget=forms.SelectDateWidget(years=YEARS),initial=str(datetime.date.today().year)+'-01-01', required=False)
    fecha_fin = forms.DateField(label='Fecha final', widget=forms.SelectDateWidget(years=YEARS),initial=str(datetime.date.today()),required=False)

class BusquedaDeclaracionExtForm(forms.Form):
    TIPO_FECHAS_CHOICES = [
        ('ingreso', 'Fecha de Ingreso'),
        ('nacimiento', 'Fecha de nacimiento'),
        ('ninguno', 'Ninguno'),
    ]
    EXT_CHOICES = [
        (None, 'Todas'),
        (False, 'Ordinaria'),
        (True, 'Extemporanea')
    ]
    nombre = forms.CharField(max_length=128,label="Nombre", required=False )
    apellido1 = forms.CharField(max_length=128,label="Primer Apellido", required=False )
    apellido2 = forms.CharField(max_length=128,label="Segundo Apellido", required=False )
    rfc = forms.CharField(max_length=13,label="RFC", required=False,validators=[RegexValidator('^([A-Z,Ñ,&]{3,4}([0-9]{2})(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])[A-Z|\d]{3})$', message="Introduzca un RFC válido")] )
    curp = forms.CharField(max_length=18,label="CURP", required=False )
    ente = forms.ModelChoiceField(queryset=CatEntesPublicos.objects.all(),required=False,label="Ente público")
    estatus = forms.ChoiceField(choices = TRUE_FALSE_CHOICES, label="Estatus",
                              initial='', widget=forms.Select(), required=False)
    dec_status = forms.ChoiceField(choices = EXT_CHOICES, label="Estatus declaración",
                              initial=None, widget=forms.RadioSelect, required=False)
    page = forms.CharField(widget=forms.HiddenInput(), required=False)
    page_size = forms.CharField(widget=forms.HiddenInput(), required=False,initial="10" )
    
class BusquedaUsuariosForm(forms.Form):
    nombre = forms.CharField(max_length=128,label="Nombre", required=False )
    apellido1 = forms.CharField(max_length=128,label="Primer Apellido", required=False )
    apellido2 = forms.CharField(max_length=128,label="Segundo Apellido", required=False )
    rfc = forms.CharField(max_length=13,label="RFC", required=False)
    estatus = forms.ChoiceField(choices = TRUE_FALSE_CHOICES, label="Estatus",
                              initial='', widget=forms.Select(), required=False)
    puesto_str = forms.CharField(max_length=128,label="Puesto", required=False )
    page = forms.CharField(widget=forms.HiddenInput(), required=False)
    page_size = forms.CharField(widget=forms.HiddenInput(), required=False,initial="10")

class BusquedaDeclaracionForm(forms.Form):
    folio = forms.CharField(max_length=128,label="Folio", required=False )
    tipo = forms.ModelChoiceField(queryset=CatTiposDeclaracion.objects.filter(codigo__in=['INICIAL', 'MODIFICACIÓN', 'CONCLUSIÓN']),label="Tipo de declaración", required=False )
    estatus = forms.ModelChoiceField(queryset=CatEstatusDeclaracion.objects.all(),label="Estatus", required=False )
    page = forms.CharField(widget=forms.HiddenInput(), required=False)
    page_size = forms.CharField(widget=forms.HiddenInput(), required=False,initial="10")

    fecha_inicio = forms.DateField(label='Fecha inicial', widget=forms.SelectDateWidget(years=YEARS),initial=str(datetime.date.today().year)+'-01-01', required=False)
    fecha_fin = forms.DateField(label='Fecha final', widget=forms.SelectDateWidget(years=YEARS),initial=str(datetime.date.today()),required=False)

class RegistroUsuarioOICForm(forms.Form):
    roles = (
        (False, 'Operador'),
        (True, 'Administrador')
    )
    estatus = (
        (True, 'Activo'),
        (False, 'Inactivo')
    )
    nombres = forms.CharField(required = True,label="NOMBRES(s)")
    apellido1 = forms.CharField(required = True,label="PRIMER APELLIDO")
    apellido2 = forms.CharField(required = False,label="SEGUNDO APELLIDO")
    nombre_ente_publico = forms.CharField(required = True,label="NOMBRE ENTE PÚBLICO")
    telefono = forms.CharField(max_length=15,required = True,label="TELÉFONO",validators=[RegexValidator('^\+?1?\d{9,10}$', message="Introduzca un Teléfono válido")])
    rfc = forms.CharField(max_length=13, label="RFC CON HOMOCLAVE", required=True,validators=[RegexValidator('^([A-Z,Ñ,&]{3,4}([0-9]{2})(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])[A-Z|\d]{3})$', message="Introduzca un RFC válido")])
    cat_areas = forms.ModelChoiceField(queryset=CatAreas.objects.all(),required=True, label="" )
    cat_puestos = forms.ModelChoiceField(queryset=CatPuestos.objects.all(),required=True, label="" )
    email = forms.EmailField(required=True, label="CORREO ELECTRÓNICO")
    rol =  forms.ChoiceField(choices=roles, label="ROL")
    estatus =  forms.ChoiceField(choices=estatus, label="ESTATUS")
    fecha_inicio = forms.DateField(label='Fecha inicial', widget=forms.SelectDateWidget(years=YEARS),initial=str(datetime.date.today().year)+'-01-01', required=False)
    id = forms.CharField(widget=forms.HiddenInput(),required=False)

    def clean(self):
        super().clean()

        try:
            id =int(self.cleaned_data.get("id"))
        except:
            id=None

        email = self.cleaned_data.get("email")
        email = str(email).lower()
        if id is None:
            if User.objects.filter(email = email).count()>0:
                self.add_error("email","Correo ya registrado")
        else:
            if User.objects.filter(email = email).exclude(pk=id).count()>0:
                self.add_error("email","Correo ya registrado")

        rfc = self.cleaned_data.get("rfc")
        rfc = str(rfc).upper()
        if id is None:
            if User.objects.filter(username = rfc).count()>0:
                self.add_error("rfc","RFC ya registrado")
        else:
            if User.objects.filter(username = rfc,pk=id).exclude(pk=id).count()>0:
                self.add_error("rfc","RFC ya registrado")

class RegistroUsuarioDeclaranteForm(forms.ModelForm):
    username = forms.CharField(max_length=13,label="RFC", required=True,validators=[RegexValidator('^([A-Z,Ñ,&]{3,4}([0-9]{2})(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])[A-Z|\d]{3})$', message="Introduzca un RFC válido")] )
    email = forms.EmailField(required=True, label="Dirección de correo electrónico")
    first_name = forms.CharField(required = True,label="Nombre")
    last_name = forms.CharField(required = True,label="Apellido")

    class Meta:
        model = User
        fields = ('username', 'first_name' , 'last_name', 'email', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True


class BusquedaGraficasForm(forms.Form):
    YEARS= [x for x in range(2000,datetime.date.today().year+1)]
    anio_filtro = forms.DateField(label='Fecha para filtro de datos', widget=forms.SelectDateWidget(years=YEARS),initial=str(datetime.date.today().year)+'-01-01', required=False)