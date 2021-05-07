from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from declaracion.models import (BienesMuebles, BienesInmuebles,
                                MueblesNoRegistrables, Inversiones,
                                Fideicomisos,
                                ActivosBienes, BienesPersonas)
from declaracion.models.catalogos import (CatTipoPersona, CatTiposMuebles, CatTiposRelacionesPersonales,CatTipoParticipacion)
import datetime

YEARS= [x for x in range(1920,datetime.date.today().year+1)]

class ActivosBienesForm(forms.ModelForm):
    class Meta:
        model = ActivosBienes
        exclude = '__all__'


class BienesPersonasForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BienesPersonasForm, self).__init__(*args, **kwargs)
        self.fields['tipo_relacion'].queryset = CatTiposRelacionesPersonales.objects.filter(codigo__in=['ABU','BISA','BISN','CONB','CONC','CONY','CUN','HER','HIJ','MAD','PAD','PRI','SOB','SUE','TATA','TATN','TIOA','NIE','NIN','OTRO'])
    class Meta:
        model = BienesPersonas
        fields = '__all__'
        exclude = ['info_personal_var', 'activos_bienes',
                   'otra_persona', 'cat_tipo_participacion']


class BienesMueblesForm(forms.ModelForm):
    fecha_adquisicion= forms.DateField(label='Fecha de contrato', widget=forms.SelectDateWidget(years=YEARS), required=False)

    def __init__(self, *args, **kwargs):
        super(BienesMueblesForm, self).__init__(*args, **kwargs)
        self.fields['cat_tipos_muebles'].queryset = CatTiposMuebles.objects.filter(codigo__in=["MECA","APAE","JOYAS","COLEC","OBRA","OTRO"])

    class Meta:
        model = BienesMuebles
        fields = '__all__'
        exclude = ['declaraciones', 'observaciones', 'activos_bienes']
        widgets = {'fecha_adquisicion': DatePickerInput(options={
            "format": 'YYYY-MM-DD',
            "locale": "es",
            "ignoreReadonly": True,
            "maxDate": 'now'
        })}

class BienesInmueblesForm(forms.ModelForm):
    fecha_contrato_compra= forms.DateField(label='Fecha de contrato', widget=forms.SelectDateWidget(years=YEARS), required=False)
    fecha_adquisicion= forms.DateField(label='Fecha de adquisicion', widget=forms.SelectDateWidget(years=YEARS), required=False)
    class Meta:
        model = BienesInmuebles
        fields = '__all__'
        exclude = ['declaraciones', 'domicilios', 'observaciones',
                   'activos_bienes']

class MueblesNoRegistrablesForm(forms.ModelForm):
    fecha_adquisicion= forms.DateField(label='Fecha de fecha de adquisicion', widget=forms.SelectDateWidget(years=YEARS), required=False)
    def __init__(self, *args, **kwargs):
        super(MueblesNoRegistrablesForm, self).__init__(*args, **kwargs)
        self.fields['cat_tipos_muebles'].queryset = CatTiposMuebles.objects.filter(codigo__in=["AUMOT","AERN","BARYA","OTRO"])
    class Meta:
        model = MueblesNoRegistrables
        fields = '__all__'
        exclude = ['declaraciones', 'observaciones', 'activos_bienes']
        widgets = {'fecha_adquisicion': DatePickerInput(options={
            "format": 'YYYY-MM-DD',
            "locale": "es",
            "ignoreReadonly": True,
            "maxDate": 'now'
        })}

class InversionesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InversionesForm, self).__init__(*args, **kwargs)
        self.fields['cat_tipo_persona'].queryset = CatTipoPersona.objects.filter(codigo__in=["DEC","CYG","CBN","CVV","DEN","CTER"])
    
    class Meta:
        model = Inversiones
        fields = '__all__'
        exclude = ['declaraciones', 'domicilios', 'observaciones',
                   'info_personal_var']
        widgets = {'fecha_inicio': DatePickerInput(options={
            "format": 'YYYY-MM-DD',
            "locale": "es",
            "ignoreReadonly": True,
            "maxDate": 'now'
        })}


class FideicomisosForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FideicomisosForm, self).__init__(*args, **kwargs)
        self.fields['tipo_persona'].queryset = CatTipoPersona.objects.filter(codigo__in=["FIDEICOMITENTE","FIDUCIARIO","FIDEICOMISARIO","COMITE_TECNICO"])
        self.fields['tipo_relacion'].queryset = CatTiposRelacionesPersonales.objects.filter(codigo__in=["DECLARANTE","DEPENDIENTE_ECONOMICO","PAREJA"])
        self.fields['cat_tipo_participacion'].queryset = CatTipoParticipacion.objects.filter(codigo__in=["FIDECOMITENTE","FIDECOMISARIO","FIDUCIARIO","COMITE_TECNICO"])
    class Meta:
        model = Fideicomisos
        fields = '__all__'
        exclude = ['declaraciones', 'observaciones',
                   'domicilio_fideicomisario', 'domicilio_fideicomitente',
                   'domicilio_fiduciario', 'activos_bienes']
        widgets = {'fecha_creacion': DatePickerInput(options={
            "format": 'YYYY-MM-DD',
            "locale": "es",
            "ignoreReadonly": True,
            "maxDate": 'now'
        })}
