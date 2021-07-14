from django.db import models
from django.urls import reverse_lazy
from .informacion_personal import(Declaraciones, Domicilios, Observaciones, InfoPersonalVar)
from .catalogos import (CatTiposPasivos, CatTiposOperaciones, CatTiposAcreedores,
                        CatTiposAdeudos, CatPaises, CatSectoresIndustria,
                        CatMonedas, CatTiposTitulares, CatUnidadesTemporales, CatTiposInmuebles, 
                        CatTipoPersona, CatTiposRelacionesPersonales, CatTiposMuebles,CatEntidadesFederativas) # agregados varios   

TIPOS_VEHICULOS = [
    ('Automóvil','Automóvil'), 
    ('Motocicleta','Motocicleta'), 
    ('Aeronave','Aeronave'), 
    ('Barco/Yate','Barco/Yate'),
    ('Otro', 'Otro (Especifique)')
]

TIPO_COMODATO = [
    ('INMUEBLE','INMUEBLE'), ('MUEBLE','VEHÍCULO (Mueble)')
]

TIPO_PERSONA = [
    ('FISICA','FISICA'), ('MORAL','MORAL')
]

# basado en https://docs.google.com/spreadsheets/d/19Kyq46YwJk9wM7znYLQdLEKfAF8jTF4WmGJINXd9Lwg/edit?ts=5d88f08f#gid=0
class PrestamoComodato(models.Model):
    """
    Class Modelo que guarda información de un bien(inmueble, vehiculo) prestado por un tercero y que el declarante use si existiese

    Methods
    ---------
    columna_uno(self),columna_dos(self) y columna(self)
        Obtienen los campos de registros ya guardados que son mostrados en la tabla de inicio de una seccion en los templates

    url_editar(self)
        Función que permite la edición de un registro de la tabla que se muestra al inicio de una sección en los templates

    url_borrar(self)
        Función que permite borrar un registro de la tabla que se muestra al inicio de una sección en los templates
    """
    otra_operacion = models.CharField(max_length=255, blank=True)
    cat_tipos_operaciones = models.ForeignKey(CatTiposOperaciones, on_delete=models.DO_NOTHING, null=True, blank=True)
    tipo_obj_comodato = models.CharField(max_length=100, choices=TIPO_COMODATO, blank=True, null=True)
    cat_tipos_inmueble = models.ForeignKey(CatTiposInmuebles, on_delete=models.DO_NOTHING, null=True, blank=True) # aqui se pones si es carro o no
    otro_tipo_inmueble = models.CharField(max_length=100, blank=True, null=True) 
    inmueble_domicilios = models.ForeignKey(Domicilios, on_delete=models.DO_NOTHING,  blank=True, null=True)
    cat_tipos_muebles = models.ForeignKey(CatTiposMuebles, on_delete=models.DO_NOTHING, null=True, blank=True) #/MODIFICADO 19/02/2020
    otro_tipo_mueble = models.CharField(max_length=255, blank=True) 
    mueble_marca = models.CharField(max_length=255, blank=True)
    mueble_anio = models.IntegerField(blank=True,null=True)
    mueble_modelo = models.CharField(max_length=255,blank=True, null=True)
    mueble_num_serie = models.CharField(max_length=255, blank=True)
    mueble_num_registro = models.CharField(max_length=255, blank=True)
    titular_infopersonalVar = models.ForeignKey(InfoPersonalVar, on_delete=models.DO_NOTHING, blank=True,null=True)
    titular_relacion = models.ForeignKey(CatTiposRelacionesPersonales, on_delete=models.DO_NOTHING, blank=True,null=True)
    otro_tipo_relacion = models.CharField(max_length=255, blank=True)#/AGREGADO 19/02/2020
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING, blank=True)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING, blank=True,null=True)
    otro_tipo_adeudo = models.CharField(max_length=255, blank=True, default="Comodato")
    cat_paises = models.ForeignKey(CatPaises, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_entidades_federativas = models.ForeignKey(CatEntidadesFederativas, on_delete=models.DO_NOTHING, null=True, blank=True)
    campo_default = models.BooleanField(blank=True, null=True, default=0)

    def columna_uno(self):
        if self.cat_tipos_operaciones:
            return u"{}".format(self.cat_tipos_operaciones)
        else:
            return u""

    def columna_dos(self):
        if self.tipo_obj_comodato:
            return u"{}".format(self.tipo_obj_comodato)
        else:
            return u""

    def columna_tres(self):
        if self.titular_relacion:
            return u"{}".format(self.titular_relacion)
        else:
            return u""

    def observacion(self):
        return [self.observaciones]

    def titular(self):
        return [self.titular_infopersonalVar]

    def url(self):
        return u"prestamoComodato"

    def url_editar(self):
        return reverse_lazy('declaracion:' + self.url() + '-editar', kwargs={'folio': self.declaraciones.folio,'pk': self.id})

    def url_borrar(self):
        return reverse_lazy('declaracion:' + self.url() + '-borrar', kwargs={'folio': self.declaraciones.folio, 'pk': self.id})
        
    def url_todos(self):
        return reverse_lazy('declaracion:' + self.url() + '', kwargs={'folio': self.declaraciones.folio})

    def tipo_operacion(self):
        try:
            if self.cat_tipos_operaciones.default:
                return u"{} {}".format(self.cat_tipos_operaciones,
                                       self.otra_operacion)
            else:
                return u"{}".format(self.cat_tipos_operaciones)
        except Exception as e:
            return u""
            

class DeudasOtros(models.Model):
    """
    Class Modelo que guarda información de las deudas del declarante(Sección: Adeudos/Pasivos)

    Methods
    ---------
    columna_uno(self),columna_dos(self) y columna(self)
        Obtienen los campos de registros ya guardados que son mostrados en la tabla de inicio de una seccion en los templates

    url_editar(self)
        Función que permite la edición de un registro de la tabla que se muestra al inicio de una sección en los templates

    url_borrar(self)
        Función que permite borrar un registro de la tabla que se muestra al inicio de una sección en los templates
    """
    otra_operacion = models.CharField(max_length=255, blank=True)
    otro_tipo_acreedor = models.CharField(max_length=255, blank=True)
    otro_tipo_adeudo = models.CharField(max_length=255, blank=True)
    numero_cuenta = models.CharField(max_length=255, blank=True)
    fecha_generacion = models.DateField(null=True, blank=True)
    monto_original = models.IntegerField(null=True, blank=True, default=0)
    tasa_interes = models.IntegerField(null=True, blank=True, default=0)
    saldo_pendiente = models.IntegerField(null=True, blank=True,default=0)
    monto_abonado = models.IntegerField(null=True, blank=True,default=0)
    plazo = models.IntegerField(null=True, blank=True, default=0)
    otro_titular = models.CharField(max_length=255, blank=True)
    porcentaje_adeudo = models.IntegerField(null=True, blank=True,default=0)
    garantia = models.BooleanField(blank=True, null=True, default=0)
    nombre_garantes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cat_monedas = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_paises = models.ForeignKey(CatPaises, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_acreedores = models.ForeignKey(CatTiposAcreedores, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_adeudos = models.ForeignKey(CatTiposAdeudos, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_operaciones = models.ForeignKey(CatTiposOperaciones, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_pasivos = models.ForeignKey(CatTiposPasivos, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_titulares = models.ForeignKey(CatTiposTitulares, on_delete=models.DO_NOTHING, null=True, blank=True)
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING)
    cat_unidades_temporales = models.ForeignKey(CatUnidadesTemporales, on_delete=models.DO_NOTHING, null=True, blank=True)
    tercero_infopersonalvar = models.ForeignKey(InfoPersonalVar, on_delete=models.DO_NOTHING, null=True, blank=True)
    acredor_es_fisica = models.BooleanField(blank=True, null=True, default=None)
    acreedor_nombre = models.CharField(max_length=255, null=True, blank=True)
    acreedor_rfc = models.CharField(max_length=255, null=True, blank=True)

    def observacion(self):
        return [self.observaciones]

    def persona(self):
        return [self.acreedor_infopersonalvar]

    def columna_uno(self):
        if self.cat_tipos_operaciones:
            return u"{}".format(self.cat_tipos_operaciones)
        else:
            return u""

    def columna_dos(self):
        if self.cat_tipos_titulares:
            return u"{}".format(self.cat_tipos_titulares)
        else:
            return u""

    def columna_tres(self):
        if self.cat_tipos_adeudos:
            return u"{}".format(self.cat_tipos_adeudos)
        else:
            return u""

    def url(self):
        if self.cat_tipos_pasivos_id == 1:
            return u"deudas"
        else:
            return u"deudas-otros"

    def url_editar(self):
            return reverse_lazy('declaracion:' + self.url() + '-editar',
                                kwargs={'folio': self.declaraciones.folio,
                                        'pk': self.id})

    def url_borrar(self):
        return reverse_lazy('declaracion:' + self.url() + '-borrar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_todos(self):
        return reverse_lazy('declaracion:' + self.url() + '',
                            kwargs={'folio': self.declaraciones.folio})

    def tipo_operacion(self):
        try:
            if self.cat_tipos_operaciones.default:
                return u"{} {}".format(self.cat_tipos_operaciones,
                                       self.otra_operacion)
            else:
                return u"{}".format(self.cat_tipos_operaciones)
        except Exception as e:
            return u""

    def tipo_acreedor(self):
        try:
            if self.cat_tipos_acreedores.default:
                return u"{} {}".format(self.cat_tipos_acreedores,
                                       self.otro_tipo_acreedor)
            else:
                return u"{}".format(self.cat_tipos_acreedores)
        except Exception as e:
            return u""

    def tipo_adeudo(self):
        try:
            if self.cat_tipos_adeudos.default:
                return u"{} {}".format(self.cat_tipos_adeudos,
                                       self.otro_tipo_adeudo)
            else:
                return u"{}".format(self.cat_tipos_adeudos)
        except Exception as e:
            return u""

    def titular(self):
        try:
            if self.cat_tipos_titulares.default:
                return u"{} {}".format(self.cat_tipos_titulares,
                                       self.otro_titular)
            else:
                return u"{}".format(self.cat_tipos_titulares)
        except Exception as e:
            return u""
