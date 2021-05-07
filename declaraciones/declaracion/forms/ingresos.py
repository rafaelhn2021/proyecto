from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.forms import  TextInput,Textarea
from declaracion.models import IngresosDeclaracion
import datetime

YEARS= [x for x in range(1920,datetime.date.today().year+1)]

class IngresosDeclaracionForm(forms.ModelForm):
    fecha_ingreso= forms.DateField(label='Fecha de nacimiento', widget=forms.SelectDateWidget(years=YEARS), required=False)
    fecha_conclusion= forms.DateField(label='Fecha de nacimiento', widget=forms.SelectDateWidget(years=YEARS),required=False)
    
    def __init__(self, *args, **kwargs):
        super(IngresosDeclaracionForm, self).__init__(*args, **kwargs)
        self.fields['ingreso_mensual_otros_ingresos'].widget.attrs['readonly'] = True
        self.fields['ingreso_mensual_neto'].widget.attrs['readonly'] = True
        #self.fields['ingreso_mensual_pareja_dependientes'].widget.attrs['readonly'] = True
        self.fields['ingreso_mensual_total'].widget.attrs['readonly'] = True

    def clean(self):
        fecha_ingreso = self.cleaned_data.get('fecha_ingreso')
        fecha_salida = self.cleaned_data.get('fecha_conclusion')

        if fecha_ingreso and fecha_salida:
            if fecha_ingreso > fecha_salida:
                raise forms.ValidationError("FECHA INGRESO: Fecha de ingreso no puede ser superior a la fecha de conclusión")

    class Meta:
        model = IngresosDeclaracion
        fields = '__all__'
        exclude = ['declaraciones', 'observaciones']
        widgets = {
            'tipo_servicio': Textarea(attrs={'rows': 4})
        }