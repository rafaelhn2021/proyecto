from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from declaracion.models import (Membresias,
                                Representaciones, SociosComerciales,
                                ClientesPrincipales,
                                BeneficiosGratuitos, Apoyos)
from declaracion.models.catalogos import (CatTiposRelacionesPersonales,CatTipoPersona)
from django.forms import  TextInput,Textarea
import datetime

YEARS= [x for x in range(1920,datetime.date.today().year+1)]

class MembresiasForm(forms.ModelForm):
    fecha_inicio = forms.DateField(label='Fecha de nacimiento', widget=forms.SelectDateWidget(years=YEARS))

    def __init__(self, *args, **kwargs):
        super(MembresiasForm, self).__init__(*args, **kwargs)
        self.fields['tipoRelacion'].queryset = CatTiposRelacionesPersonales.objects.filter(codigo__in=["DECLARANTE","PAREJA","DEPENDIENTE_ECONOMICO"])

    class Meta:
        model = Membresias
        fields = '__all__'
        exclude = ['declaraciones', 'domicilios', 'observaciones']
        widgets = {'fecha_inicio': DatePickerInput(options={
            "format": 'YYYY-MM-DD',
            "locale": "es",
            "ignoreReadonly": True,
            "maxDate": 'now'
        })}
        
class ApoyosForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ApoyosForm, self).__init__(*args, **kwargs)
        self.fields['cat_tipos_relaciones_personales'].queryset = CatTiposRelacionesPersonales.objects.filter(codigo__in=["DC","CY","CON","CONV","HIJ","HER","CU","MA","PA","TIO","PRI","SOB","AHI","NUE","YER","ABU","NIE","OTRO"])
    class Meta:
        model = Apoyos
        fields = '__all__'
        exclude = ['declaraciones', 'observaciones', 'beneficiario_infopersonalvar']
        widgets = {
            'especifiqueApoyo': Textarea(attrs={'rows': 4})
        }

class RepresentacionesActivasForm(forms.ModelForm):
    fecha_inicio= forms.DateField(label='Fecha de nacimiento', widget=forms.SelectDateWidget(years=YEARS))
    def __init__(self, *args, **kwargs):
        super(RepresentacionesActivasForm, self).__init__(*args, **kwargs)
        self.fields['cat_tipos_relaciones_personales'].queryset = CatTiposRelacionesPersonales.objects.filter(codigo__in=["DECLARANTE","PAREJA","DEPENDIENTE_ECONOMICO"])
    
    class Meta:
        model = Representaciones
        fields = '__all__'
        exclude = ['declaraciones', 'observaciones', 'info_personal_var']
        widgets = {'fecha_inicio': DatePickerInput(options={
            "format": 'YYYY-MM-DD',
            "locale": "es",
            "ignoreReadonly": True,
            "maxDate": 'now'
        })}


class SociosComercialesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SociosComercialesForm, self).__init__(*args, **kwargs)
        self.fields['tipoRelacion'].queryset = CatTiposRelacionesPersonales.objects.filter(codigo__in=["DECLARANTE","PAREJA","DEPENDIENTE_ECONOMICO"])
        self.fields['tipoParticipacion'].queryset = CatTipoPersona.objects.filter(codigo__in=["SCIO","ACCI","COMI","REPR","APOD","COLB","BENE","OTRO"])

    class Meta:
        model = SociosComerciales
        fields = '__all__'
        exclude = ['declaraciones', 'observaciones', 'socio_infopersonalvar']

class ClientesPrincipalesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClientesPrincipalesForm, self).__init__(*args, **kwargs)
        self.fields['cat_tipos_relaciones_personales'].queryset = CatTiposRelacionesPersonales.objects.filter(codigo__in=["DECLARANTE","PAREJA","DEPENDIENTE_ECONOMICO"])
        
    class Meta:
        model = ClientesPrincipales
        fields = '__all__'
        exclude = ['declaraciones', 'domicilios', 'observaciones',
                   'info_personal_var']

class BeneficiosGratuitosForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BeneficiosGratuitosForm, self).__init__(*args, **kwargs)
        self.fields['cat_tipos_relaciones_personales'].queryset = CatTiposRelacionesPersonales.objects.filter(codigo__in=["DC","CY","CON","CONV","HIJ","HER","CU","MA","PA","TIO","PRI","SOB","AHI","NUE","YER","ABU","NIE","OTRO"])
    class Meta:
        model = BeneficiosGratuitos
        fields = '__all__'
        exclude = ['declaraciones', 'observaciones']
