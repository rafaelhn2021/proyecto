from django import forms
from django.core.validators import FileExtensionValidator


class ConfirmacionForm(forms.Form):
   datos_publicos = forms.TypedChoiceField(
                    coerce=lambda x: x == 'True',
                    choices=((False, 'False'), (True, 'True')),
                    widget=forms.RadioSelect,
                    required=True
                   )