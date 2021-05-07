import fileinput
from django.conf import settings
from django.contrib import admin
from .models import sitio_personalizacion, declaracion_faqs, Valores_SMTP
from django import forms
from django.forms import ModelForm, PasswordInput


class declaracion_faqs_admin(admin.ModelAdmin):
	pass

class sitio_personalizacion_admin(admin.ModelAdmin):
	#exclude = ("color_base", "color_obscuro", "color_primario", "color_secundario", "color_neutro",  "color_suceso", "color_peligro", "color_alerta")
	exclude = ("fecha_incio", "fecha_fin")

	def has_add_permission(self, request):
		count = sitio_personalizacion.objects.all().count()
		if count == 0:
			return True
		return False
	
	def has_delete_permission(self, request, obj=None):
		count = sitio_personalizacion.objects.all().count()
		if count == 0:
			return True
		return False
		
	def save_model(self, request, obj, form, change):
		obj.user = request.user
		try:
			filecss = str(settings.BASE_DIR) + "/media/personalizar/personalizar.css"
			inside = '/*** color y personalizados */.color-base { color: '+obj.color_base+' !important; }.color-obscuro { color: '+obj.color_obscuro+' !important; }.color-primario { color: '+obj.color_primario+' !important; }.color-secundario { color: '+obj.color_secundario+' !important; }.color-complemento { color: #D9EBEC !important; }.color-neutro { color: '+obj.color_neutro+' !important; }.color-suceso { color: '+obj.color_suceso+' !important; }.color-peligro { color: '+obj.color_peligro+' !important; }.color-alerta { color: '+obj.color_alerta+' !important; }.bgcolor-base { background:'+obj.color_base+' !important; }.bgcolor-obscuro { background: '+obj.color_obscuro+' !important; }.bgcolor-primario { background: '+obj.color_primario+' !important; }.bgcolor-secundario { background: '+obj.color_secundario+' !important; }.bgcolor-complemento { background: #D9EBEC !important; }.bgcolor-neutro { background: '+obj.color_neutro+' !important; }.bgcolor-suceso { background: '+obj.color_suceso+' !important; }.bgcolor-peligro { background: '+obj.color_peligro+' !important; }.bgcolor-alerta { background: '+obj.color_alerta+' !important; }.bordecolor-base { border-color:'+obj.color_base+' !important; }.bordecolor-obscuro { border-color:'+obj.color_obscuro+' !important; }.bordecolor-primario { border-color: '+obj.color_primario+' !important; }.bordecolor-secundario { border-color: '+obj.color_secundario+' !important; }.bordecolor-complemento { border-color: #D9EBEC !important; }.bordecolor-neutro { border-color: '+obj.color_neutro+' !important; }.bordecolor-suceso { border-color: '+obj.color_suceso+' !important; }.bordecolor-peligro { border-color:'+obj.color_peligro+' !important; }.bordecolor-alerta { border-color: '+obj.color_alerta+' !important; }/***     */'
			with open(filecss, 'w+') as css:
				css.write(inside)
		except Exception as e:
			obj.nombre_institucion = str(e)
		super().save_model(request, obj, form, change)



class Valores_SMTP_form(ModelForm):
    class Meta:
        model = Valores_SMTP
        fields = '__all__'
        widgets = {
            'mailpassword': PasswordInput(),
        }

class Valores_SMTP_admin(admin.ModelAdmin):
    form = Valores_SMTP_form


admin.site.register(declaracion_faqs, declaracion_faqs_admin)
admin.site.register(sitio_personalizacion, sitio_personalizacion_admin)
admin.site.register(Valores_SMTP, Valores_SMTP_admin)

