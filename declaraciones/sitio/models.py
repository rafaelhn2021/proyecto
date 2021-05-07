from django.db import models
from colorfield.fields import ColorField


class sitio_personalizacion(models.Model):
	"""
	Class modelo sitio_personalizacion integrado para realizar cambios en el diseño del sistema como logo y colores
	"""
	nombre_institucion = models.CharField("Nombre de la institución", max_length=300, default="Sin nombrar")
	siglas_sistema = models.CharField("Siglas del sistema", max_length=30, default="SN")
	direccion_calle = models.CharField("Calle, número y numero interior de la institución", max_length=300, default="Sin nombrar")
	direccion_cp = models.CharField("código postal de la institución", max_length=300, default="Sin nombrar")
	direccion_ciudad = models.CharField("ciudad de la institución", max_length=300, default="Sin nombrar")
	direccion_estado = models.CharField("estado de la institución", max_length=300, default="Jalisco")
	direccion_telefonos = models.CharField("telefonos de la institución", max_length=300, default="sn")
	direccion_correos = models.CharField("correos electrónico de la institución", max_length=300, default="sn")
	#activar_captcha = models.BooleanField("Activar o desactivar los captcha (necesitas haber dado de alta una llave correcta en el campo 'llave para el captcha de google')", default=False)
	recaptcha = models.BooleanField(default=False)
	google_captcha_sitekey = models.CharField("Clave sitio web para el captcha de Google ", max_length=300, default="6LdVTt0UAAAAAEkz8C_gBLX8F4O4cJZt762TDgvW")
	google_captcha_secretkey = models.CharField("Clave secreta captcha de Google ", max_length=300, null=True, blank=True)
	terminosCondiciones_registro = models.FileField("PDF con los terminos y condiciones al registrarse", upload_to='personalizar/', max_length=300, default='personalizar/terminos_y_Condiciones_registro.pdf')
	imagen_logo = models.ImageField("imagen logo", upload_to='personalizar/', max_length=300, default='personalizar/default_logo.png')
	imagen_sublogo = models.ImageField("imagen logo simplificado ", upload_to='personalizar/', max_length=300, default='personalizar/default_logo_simple.png')
	imagen_inicioFondo = models.ImageField("imagen fondo del index", upload_to='personalizar/', max_length=300, default='personalizar/default_fondo_index.png')
	imagen_inicioPiepagina = models.ImageField("imagen pie de página del index", upload_to='personalizar/', max_length=300, default='personalizar/default_footer_index.png')
	imagen_defaultPerfil = models.ImageField("imagen default para el perfil de usuario", upload_to='personalizar/', max_length=300, default='personalizar/default_image_perfil.png')
	color_base = models.CharField("Color base (default=#fff)", max_length=20, default="#fff")
	color_obscuro = models.CharField("Color obscuro (default=#000)", max_length=20, default="#000")
	color_primario = models.CharField("Color primario (default=#015F78)", max_length=20, default="#015F78")
	color_secundario = models.CharField("Color secundario (default=#A4B54C)", max_length=20, default="#A4B54C")
	color_neutro = models.CharField("Color neutro (default=#F2F2F2)", max_length=20, default="#F2F2F2")
	color_suceso = models.CharField("Color suceso (default=#5dffff)", max_length=20, default="#5dffff")
	color_peligro = models.CharField("Color peligro (default=#38A6F9)", max_length=20, default="#38A6F9")
	color_alerta = models.CharField("Color error (default=#dc3545)", max_length=20, default="#dc3545")
	fecha_incio = models.DateField(null=True)
	fecha_fin = models.DateField(null=True)
	declaracion_modificacion_crear = models.BooleanField("Crear declaración de modificación de manera abierta", default=True)

	class Meta:
		verbose_name = 'personalización del sitio'
		verbose_name_plural = 'personalización del sitio'

	def __str__(self):
		return self.nombre_institucion


class declaracion_faqs(models.Model):
	orden = models.IntegerField("Orden (si tiene cero es omitido)", blank=False, default=0)
	pregunta = models.CharField("Pregunta", max_length=3000, default="")
	respuesta = models.CharField("Respuesta", max_length=3000, default="")

	class Meta:
		verbose_name = "Preguntas Frecuentes sobre declaraciones"
		verbose_name_plural = "Preguntas Frecuentes sobre declaraciones"

	def __str__(self):
		return self.pregunta


class Valores_SMTP(models.Model):

	mailaddress = models.CharField("Correo", max_length=300)
	mailpassword = models.CharField("Contraseña", max_length=200)
	nombre_smtp = models.CharField("SMTP", max_length=200)
	puerto = models.IntegerField("Puerto", blank=False)

	def __str__(self):
		return "SMTP "+str(self.pk)		
