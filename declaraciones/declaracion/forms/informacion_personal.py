from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.core.validators import RegexValidator
from django.forms import  TextInput,Textarea
from declaracion.models import (Declaraciones, InfoPersonalFija, Domicilios,
                                InfoPersonalVar, Observaciones, DatosCurriculares,
                                Encargos, ExperienciaLaboral,
                                ConyugeDependientes,DeclaracionFiscal)
from declaracion.models.catalogos import (CatMunicipios,CatEntidadesFederativas,CatMonedas,
                                            CatTiposRelacionesPersonales,CatAmbitosLaborales,
                                            CatSectoresIndustria, CatAreas)
import datetime

YEARS= [x for x in range(1920,datetime.date.today().year+1)]

class DeclaracionFiscalForm(forms.ModelForm):
    class Meta:
        model = DeclaracionFiscal
        fields = '__all__'
        exclude = ['declaraciones']

class DeclaracionForm(forms.ModelForm):
    class Meta:
        model = Declaraciones
        fields = ['cat_tipos_declaracion']
        widgets = {'cat_tipos_declaracion': forms.HiddenInput()}


class InfoPersonalFijaForm(forms.ModelForm):
    fecha_inicio = forms.DateField(label='Fecha de nacimiento', widget=forms.SelectDateWidget(years=YEARS))
    class Meta:
        model = InfoPersonalFija
        fields = '__all__'



class DomiciliosForm(forms.ModelForm):
    cp=forms.CharField(max_length=5,required=False)
    class Meta:
        model = Domicilios
        fields = '__all__'


class InfoPersonalVarForm(forms.ModelForm):
    fecha_nacimiento = forms.DateField(label='Fecha de nacimiento', widget=forms.SelectDateWidget(years=YEARS), required=False)
    curp = forms.CharField(max_length=20, label="CURP (si aplica)", required=False, validators=[RegexValidator(
        '^[A-Z]{1}[AEIOU]{1}[A-Z]{2}[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])[HM]{1}(AS|BC|BS|CC|CS|CH|CL|CM|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)[B-DF-HJ-NP-TV-Z]{3}[0-9A-Z]{1}[0-9]{1}$',
        message="Introduzca un CURP válido")])
    tel_particular =  forms.CharField(max_length=15, required=False, label="Teléfono",
                               validators=[RegexValidator('^\d{4,}$', message="Introduzca un Teléfono válido")])
    tel_movil =  forms.CharField(max_length=15, required=False, label="Teléfono",
                               validators=[RegexValidator('^\d{4,}$', message="Introduzca un Teléfono válido")])
    email_personal = forms.EmailField(required=False)

    class Meta:
        model = InfoPersonalVar
        fields = '__all__'
        exclude = ['declaraciones', 'domicilios', 'observaciones',
                   'activos_bienes']

class ObservacionesForm(forms.ModelForm):
    class Meta:
        model = Observaciones
        fields = '__all__'
        widgets = {
            'observacion': Textarea(attrs={'rows': 4})
        }


class DatosCurricularesForm(forms.ModelForm):
    conclusion = forms.DateField(label='Fecha obtención del documento', widget=forms.SelectDateWidget(years=YEARS), required=False)
    class Meta:
        model = DatosCurriculares
        fields = '__all__'
        exclude = ['declaraciones', 'observaciones']


class DatosEncargoActualForm(forms.ModelForm):
    telefono_laboral = forms.CharField(max_length=15, required=False, label="Teléfono", validators=[RegexValidator('^\d{8,}$', message="Introduzca un Teléfono válido")])
    telefono_extension = forms.CharField(max_length=10, required=False, label="Teléfono",validators=[RegexValidator('^\d{2,}$', message="Introduzca una Extensión válido")])
    posesion_inicio = forms.DateField(label='Fecha de inicio de posesion', widget=forms.SelectDateWidget(years=YEARS))
    email_laboral = forms.EmailField(required=False)
    cat_areas = forms.ModelChoiceField(queryset=CatAreas.objects.all(),required=False, label="" )

    def __init__(self, *args, **kwargs):
        super(DatosEncargoActualForm, self).__init__(*args, **kwargs)
        self.fields['nombre_ente_publico'].widget.attrs['readonly'] = True
        self.fields['nivel_encargo'].widget.attrs['readonly'] = True

    class Meta:
        model = Encargos
        fields = '__all__'
        exclude = ['declaraciones', 'domicilios', 'observaciones', 'cat_sectores_industria']

class ExperienciaLaboralForm(forms.ModelForm):
    fecha_ingreso = forms.DateField(label='Fecha de ingreso', widget=forms.SelectDateWidget(years=YEARS))
    fecha_salida = forms.DateField(label='Fecha de salida', widget=forms.SelectDateWidget(years=YEARS))

    def __init__(self, *args, **kwargs):
        super(ExperienciaLaboralForm, self).__init__(*args, **kwargs)
        self.fields['cat_ambitos_laborales'].queryset = CatAmbitosLaborales.objects.filter(codigo__in=["PUB","PRV","OTR"])

    def clean(self):
        fecha_ingreso = self.cleaned_data.get('fecha_ingreso')
        fecha_salida = self.cleaned_data.get('fecha_salida')

        if fecha_ingreso > fecha_salida:
            raise forms.ValidationError("FECHA INGRESO: Fecha de ingreso no puede ser superior a la fecha de egreso")

    class Meta:
        model = ExperienciaLaboral
        fields = '__all__'
        exclude = ['declaraciones', 'domicilios', 'observaciones']
        widgets = {'fecha_ingreso': DatePickerInput(options={
            "format": 'YYYY-MM-DD',
            "locale": "es",
            "ignoreReadonly": True,
            "maxDate": 'now'
        }), 'fecha_salida': DatePickerInput(options={
            "format": 'YYYY-MM-DD',
            "locale": "es",
            "ignoreReadonly": True,
            "maxDate": 'now'
        })}


class ConyugeDependientesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ConyugeDependientesForm, self).__init__(*args, **kwargs)
        self.fields['cat_tipos_relaciones_personales'].queryset = CatTiposRelacionesPersonales.objects.filter(codigo__in=["ABU","CUN","HER","HIJ","MAD","PAD","PRI","SOB","SUE","TIOA","AHI","NUE","YER","NIE","OTRO"])
        self.fields['actividadLaboral'].queryset = CatAmbitosLaborales.objects.filter(codigo__in=["PUB","PRI","OTRO","NIN"])
    class Meta:
        model = ConyugeDependientes
        fields = '__all__'
        exclude = ['declaraciones', 'domicilios', 'observaciones',
                   'declarante_infopersonalvar', 'dependiente_infopersonalvar']


class ParejaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ParejaForm, self).__init__(*args, **kwargs)
        self.fields['cat_tipos_relaciones_personales'].queryset = CatTiposRelacionesPersonales.objects.filter(grupo_familia=1)
        self.fields['actividadLaboral'].queryset = CatAmbitosLaborales.objects.filter(codigo__in=["PUB","PRI","OTRO","NIN"])
    class Meta:
        model = ConyugeDependientes
        fields = '__all__'
        exclude = ['declaraciones', 'domicilios', 'observaciones',
                   'declarante_infopersonalvar', 'dependiente_infopersonalvar']