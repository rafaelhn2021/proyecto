from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from declaracion.models import (DeudasOtros,PrestamoComodato)
from declaracion.models.catalogos import (CatTiposMuebles,CatTiposRelacionesPersonales)
import datetime

YEARS= [x for x in range(1920,datetime.date.today().year+1)]


class PrestamoComodatoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PrestamoComodatoForm, self).__init__(*args, **kwargs)
        self.fields['cat_tipos_muebles'].queryset = CatTiposMuebles.objects.filter(codigo__in=["AUMOT","AERN","BARYA","OTRO"])#/AGREGADO 19/02/2020
        self.fields['titular_relacion'].queryset = CatTiposRelacionesPersonales.objects.filter(codigo__in=["DECLARANTE","DEPENDIENTE_ECONOMICO","PAREJA","OTRO"])#/AGREGADO 19/02/2020

    class Meta:
        model = PrestamoComodato
        fields = '__all__'
        widgets = {'fecha_generacion': DatePickerInput(options={
            "format": 'YYYY-MM-DD',
            "locale": "es",
            "ignoreReadonly": True,
            "maxDate": 'now'
        }),
        'plazo_entrega': DatePickerInput(options={
            "format": 'YYYY-MM-DD',
            "locale": "es",
            "ignoreReadonly": True,
            "maxDate": 'now'
        })}

class DeudasForm(forms.ModelForm):
    fecha_generacion = forms.DateField(label='Fecha de inicio', widget=forms.SelectDateWidget(years=YEARS))

    class Meta:
        model = DeudasOtros
        fields = '__all__'
        exclude = ['declaraciones', 'domicilios', 'observaciones',
                   'cat_tipos_pasivos', 'acreedor_infopersonalvar']
        widgets = {'fecha_generacion': DatePickerInput(options={
            "format": 'YYYY-MM-DD',
            "locale": "es",
            "ignoreReadonly": True,
            "maxDate": 'now'
        })}
