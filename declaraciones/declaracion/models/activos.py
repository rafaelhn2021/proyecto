from django.db import models
from django.urls import reverse_lazy
from .informacion_personal import(Declaraciones, Domicilios, Observaciones,
                                  InfoPersonalVar)
from .catalogos import (CatTiposInmuebles, CatTiposTitulares,
                        CatFormasAdquisiciones, CatSectoresIndustria,
                        CatMonedas, CatTiposOperaciones, CatTiposMuebles,
                        CatPaises, CatEntidadesFederativas,
                        CatTiposEspecificosInversiones, CatTiposInversiones,
                        CatTiposMetales, CatTiposFideicomisos,
                        CatTiposRelacionesPersonales, CatUnidadesTemporales, CatActivoBien,
                        CatTipoParticipacion, CatEntesPublicos, CatTipoPersona, CatMotivoBaja)

FID_DATA = [ 
    ('FIDEICOMITENTE', 'Fideicomiente'),
    ('FIDUCIARIO', 'Fiduciario'),
    ('FIDEICOMISARIO', 'Fideicomisario'),
    ('COMITE TECNICO', 'Comité técnico')

]

FORMAS_PAGO = [ 
    ('CRÉDITO', 'CRÉDITO'),
    ('CONTADO', 'CONTADO'),
    ('NO APLICA', 'NO APLICA')
]

VALOR_CONFORME_A = [ 
    ('ESCRITURA PÚBLICA', 'ESCRITURA PÚBLICA'),
    ('SENTENCIA', 'SENTENCIA'),
    ('CONTRATO', 'CONTRATO')
]

FONDOS_INVERSION = [ 
    ('SOICIEDADES DE INVERSION', 'SOICIEDADES DE INVERSION'),
    ('INVERSIONES FINANCIERAS EN EL EXTRANJERO', 'INVERSIONES FINANCIERAS EN EL EXTRANJERO')
]

ORGANIZACIONES = [ 
    ('ACCIONES','ACCIONES'),
    ('CAJAS DE AHORRO','CAJAS DE AHORRO')
]

POSESIONES = [ 
    ('CENTENARIOS','CENTENARIOS'),
    ('DIVISAS','DIVISAS'),
    ('MONEDA NACIONAL','MONEDA NACIONAL'),
    ('ONZAS TROY','ONZAS TROY'),
    ('CENTENARIOS','CENTENARIOS'),
    ('CRIPTOMONEDAS','CRIPTOMONEDAS'),
]

SEGUROS = [ 
    ('SEGURO DE SEPARACION INDIVIDUALIZADO','SEGURO DE SEPARACION INDIVIDUALIZADO'),
    ('SEGURO DE INVERSION','SEGURO DE INVERSIÓN'),
    ('SEGURO DE VIDA','SEGURO DE VIDA'),
]

VALORES = [ 
    ('ACCIONES Y DERIVADOS','ACCIONES Y DERIVADOS'),
    ('ACEPTACIONES BANCARIAS','ACEPTACIONES BANCARIAS'),
    ('BONOS GUBERNAMENTALES','BONOS GUBERNAMENTALES'),
    ('PAPEL COMERCIAL','PAPEL COMERCIAL')
]

AFORES = [ 
    ('AFORES','AFORES'),
    ('FIDEICOMISOS','FIDEICOMISOS'),
    ('CERTFICADOS DE LA TESORERIA','CERTFICADOS DE LA TESORERIA'),
    ('PRESTAMOS A FAVOR DE UN TERCERO','PRESTAMOS A FAVOR DE UN TERCERO'),
]

UNIDADES_MEDIDA = [ 
    ('m2', 'Metro cuadrado - m2'),
    ('ha', 'Hectárea - ha'),
    ('km2', 'Kilómetro cuadrado - km2')

]

class ActivosBienes(models.Model):
    """
    Class Modelo que guarda información de los activos Bienes
    ---------
    Las variables declaradas en este modelo(ej.BIENES_INMUEBLES=1) corresponden a los ID del catálogo catActivoBien
    Maneja el tipo del tipo de activo
    """
    BIENES_INMUEBLES = 1
    BIENES_INTANGIBLES = 2
    BIENES_MUEBLES = 3
    MUEBLES_NO_REGISTRABLES = 4
    FIDEICOMISOS = 5
    CUENTAS_POR_COBRAR = 6
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING)
    id_activobien = models.IntegerField(null=True)
    cat_activo_bien = models.ForeignKey(CatActivoBien, on_delete=models.DO_NOTHING, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BienesPersonas(models.Model):
    """ 
    Class Modelo que guarda la relación de la persona con el bien que posee 
    ---------
    Las variables declaradas en este modelo(ej.COVENDEDOR=1) corresponden a los ID del catálogo CatTipoParticipacion
    Contiene el tipo de persona con respecto al activo
    """
    COVENDEDOR = 1
    FIDEICOMITENTE = 3
    FIDEICOMISARIO = 4
    FIDUCIARIO = 5
    PRESTATARIO_O_DEUDOR = 6
    DECLARANTE = 7
    COPROPIETARIO = 8
    PROPIETARIO_ANTERIOR = 10
    info_personal_var = models.ForeignKey(InfoPersonalVar, on_delete=models.DO_NOTHING, related_name="bienes_personas_info_personal_var", verbose_name="Información Personal")
    activos_bienes = models.ForeignKey(ActivosBienes, on_delete=models.DO_NOTHING, verbose_name="Activos Bienes")
    porcentaje = models.IntegerField(null=True, blank=True, verbose_name="Porcentaje (%)", default=0)
    es_propietario = models.BooleanField(blank=True, null=True, default=None, verbose_name="Es propietario")
    precio_adquision = models.IntegerField(null=True, blank=True, verbose_name="Precio de Adquisición",default=0)
    el_adquirio = models.BooleanField(blank=True, null=True, default=None, verbose_name="el adquirio")
    cat_tipo_participacion = models.ForeignKey(CatTipoParticipacion, on_delete=models.DO_NOTHING, verbose_name="Tipo de perticipación")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")
    tipo_relacion = models.ForeignKey(CatTiposRelacionesPersonales, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name="Tipo de relación")
    otra_relacion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Otra tipo de relación")
    otra_relacion_familiar = models.CharField(max_length=255, blank=True, verbose_name="Otro tipo de relación familiar")
    otra_persona = models.ForeignKey(InfoPersonalVar, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="bienes_personas_otra_persona", verbose_name="Información Personal de la otra persona")

    def tipo(self):
        return self.cat_tipo_participacion_id

    def relacion(self):
        try:
            if self.tipo_relacion.default:
                return u"{} {}".format(self.tipo_relacion,
                                       self.otra_relacion)
            else:
                return u"{}".format(self.tipo_relacion)
        except Exception as e:
            return u""


class BienesInmuebles(models.Model):
    """
    Class Modelo que guarda información de los inmubles que posea el declarante
    
    Methods
    -------------
    persona(self)
        Obtiene el primer registro donde el tipo de participación sea igual a la variable(COPROPIETARIO) declarada en el modelo BienesInmuebles

    copropietario(self)
        Obtiene información de los coopropietarios

    declarante(self)
        Obtiene información del declante

    propierario_anterior(self)
        Obtiene información del propietario anterior

    columna_uno(self),columna_dos(self) y columna(self)
        Obtienen los campos de registros ya guardados que son mostrados en la tabla de inicio de una seccion en los templates

    url_editar(self)
        Función que permite la edición de un registro de la tabla que se muestra al inicio de una sección en los templates

    url_borrar(self)
        Función que permite borrar un registro de la tabla que se muestra al inicio de una sección en los templates

    """
    superficie_terreno = models.IntegerField(null=True, blank=True,default=0)
    unidad_medida_terreno = models.CharField(max_length=255, null=True, blank=True,choices=UNIDADES_MEDIDA)
    superficie_construccion = models.IntegerField(null=True, blank=True,default=0)
    unidad_medida_construccion = models.CharField(max_length=255, null=True, blank=True,choices=UNIDADES_MEDIDA)
    otro_titular = models.CharField(max_length=255, blank=True)
    num_escritura_publica = models.CharField(max_length=255, blank=True)
    num_registro_publico = models.CharField(max_length=255, blank=True)
    folio_real = models.CharField(max_length=255, blank=True)
    fecha_contrato_compra = models.DateField(null=True, blank=True)
    otra_forma = models.CharField(max_length=255, blank=True)
    fecha_adquisicion = models.DateField(null=True, blank=True)
    forma_pago = models.CharField(max_length=255, blank=True, choices=FORMAS_PAGO)
    precio_adquisicion = models.IntegerField(null=True, blank=True,default=0)
    valor_catastral = models.IntegerField(null=True, blank=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cat_formas_adquisiciones = models.ForeignKey(CatFormasAdquisiciones, on_delete=models.DO_NOTHING, null=True, blank=True)
    valor_conforme_a = models.CharField(max_length=255, null=True, blank=True,choices=VALOR_CONFORME_A)
    cat_monedas = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_inmuebles = models.ForeignKey(CatTiposInmuebles, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_operaciones = models.ForeignKey(CatTiposOperaciones, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_titulares = models.ForeignKey(CatTiposTitulares, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_motivo_baja = models.ForeignKey(CatMotivoBaja, on_delete=models.DO_NOTHING, null=True, blank=True)#/AGREGADO
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING)
    domicilios = models.ForeignKey(Domicilios, on_delete=models.DO_NOTHING)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING)
    activos_bienes = models.ForeignKey(ActivosBienes, on_delete=models.DO_NOTHING)
    otra_operacion = models.CharField(max_length=255, blank=True, null=True)
    otro_inmueble = models.CharField(max_length=255, blank=True, null=True)
    otro_motivo = models.CharField(max_length=255, blank=True)#/AGREGADO

    def declarante(self):
        try:
            return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.DECLARANTE).first().info_personal_var
        except Exception as e:
            return None

    def declarante_bp(self):
        try:
            return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.DECLARANTE).first()
        except Exception as e:
            return None

    def copropietario(self):
        try:
            return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.COPROPIETARIO)
        except Exception as e:
            return None

    def propietario_anterior(self):
        try:
            return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.PROPIETARIO_ANTERIOR)
        except Exception as e:
            return None

    def observacion(self):
        return [self.observaciones]

    def columna_uno(self):
        if self.cat_tipos_operaciones:
            return u"{}".format(self.cat_tipos_operaciones)
        else:
            return u""

    def columna_dos(self):
        if self.cat_formas_adquisiciones:
            return u"{}".format(self.cat_formas_adquisiciones)
        else:
            return u""

    def columna_tres(self):
        if self.cat_tipos_titulares:
            return u"{}".format(self.cat_tipos_titulares)
        else:
            return u""

    def url_editar(self):
        return reverse_lazy('declaracion:bienes-inmuebles-editar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_borrar(self):
        return reverse_lazy('declaracion:bienes-inmuebles-borrar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_todos(self):
        return reverse_lazy('declaracion:bienes-inmuebles',
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

    def tipo_inmueble(self):
        try:
            if self.cat_tipos_inmuebles.default:
                return u"{} {}".format(self.cat_tipos_inmuebles,
                                       self.otro_inmueble)
            else:
                return u"{}".format(self.cat_tipos_inmuebles)
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

    @property
    def forma_adquisicion(self):
        try:
            if self.cat_formas_adquisiciones.default:
                return u"{} {}".format(self.cat_formas_adquisiciones,
                                       self.otra_forma)
            else:
                return u"{}".format(self.cat_formas_adquisiciones)
        except Exception as e:
            return u""


class BienesMuebles(models.Model):
    """
    Class Modelo que guarda información de los muebles que posea el declarante
    
    Methods
    -------------
    persona(self)
        Obtiene el primer registro donde el tipo de participación sea igual a la variable(COPROPIETARIO) declarada en el modelo BienesInmuebles

    copropietario(self)
        Obtiene información de los coopropietarios

    declarante(self)
        Obtiene información del declante

    propierario_anterior(self)
        Obtiene información del propietario anterior

    columna_uno(self),columna_dos(self) y columna(self)
        Obtienen los campos de registros ya guardados que son mostrados en la tabla de inicio de una seccion en los templates

    url_editar(self)
        Función que permite la edición de un registro de la tabla que se muestra al inicio de una sección en los templates

    url_borrar(self)
        Función que permite borrar un registro de la tabla que se muestra al inicio de una sección en los templates

    """
    otra_operacion = models.CharField(max_length=255, blank=True)
    otro_tipo_mueble = models.CharField(max_length=255, blank=True)
    otro_titular = models.CharField(max_length=255, blank=True)
    otra_forma = models.CharField(max_length=255, blank=True)
    fecha_adquisicion = models.DateField(null=True, blank=True)
    precio_adquisicion = models.IntegerField(null=True, blank=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    descripcion_bien = models.CharField(max_length=255, blank=True)
    cat_entidades_federativas = models.ForeignKey(CatEntidadesFederativas, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_formas_adquisiciones = models.ForeignKey(CatFormasAdquisiciones, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_monedas = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_paises = models.ForeignKey(CatPaises, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_muebles = models.ForeignKey(CatTiposMuebles, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_operaciones = models.ForeignKey(CatTiposOperaciones, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_titulares = models.ForeignKey(CatTiposTitulares, on_delete=models.DO_NOTHING, null=True, blank=True)
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING)
    activos_bienes = models.ForeignKey(ActivosBienes, on_delete=models.DO_NOTHING)
    forma_pago = models.CharField(max_length=255, blank=True, choices=FORMAS_PAGO)
    cat_motivo_baja = models.ForeignKey(CatMotivoBaja, on_delete=models.DO_NOTHING, null=True, blank=True)

    def declarante(self):
        try:
            return [BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.DECLARANTE).first().info_personal_var]
        except Exception as e:
            return None

    def copropietario(self):
        try:
            return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.COPROPIETARIO)
        except Exception as e:
            return None

    def propietario_anterior(self):
        try:
            return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.PROPIETARIO_ANTERIOR)
        except Exception as e:
            return None

    def observacion(self):
        return [self.observaciones]

    def columna_uno(self):
        if self.cat_tipos_operaciones:
            return u"{}".format(self.cat_tipos_operaciones)
        else:
            return u""

    def columna_dos(self):
        if self.cat_formas_adquisiciones:
            return u"{}".format(self.cat_formas_adquisiciones)
        else:
            return u""

    def columna_tres(self):
        if self.cat_tipos_titulares:
            return u"{}".format(self.cat_tipos_titulares)
        else:
            return u""

    def url_editar(self):
        return reverse_lazy('declaracion:bienes-muebles-editar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_borrar(self):
        return reverse_lazy('declaracion:bienes-muebles-borrar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_todos(self):
        return reverse_lazy('declaracion:bienes-muebles',
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

    def tipo_mueble(self):
        try:
            if self.cat_tipos_muebles.default:
                return u"{} {}".format(self.cat_tipos_muebles,
                                       self.otro_tipo_mueble)
            else:
                return u"{}".format(self.cat_tipos_muebles)
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

    def forma_adquisicion(self):
        try:
            if self.cat_formas_adquisiciones.default:
                return u"{} {}".format(self.cat_formas_adquisiciones,
                                       self.otra_forma)
            else:
                return u"{}".format(self.cat_formas_adquisiciones)
        except Exception as e:
            return u""


class MueblesNoRegistrables(models.Model):
    """
    Class Modelo que guarda información de los muebles no registrables(Usado para la sección de vehiculos) que posea el declarante
    
    Methods
    -------------
    persona(self)
        Obtiene el primer registro donde el tipo de participación sea igual a la variable(COPROPIETARIO) declarada en el modelo BienesInmuebles

    copropietario(self)
        Obtiene información de los coopropietarios

    declarante(self)
        Obtiene información del declante

    propierario_anterior(self)
        Obtiene información del propietario anterior

    columna_uno(self),columna_dos(self) y columna(self)
        Obtienen los campos de registros ya guardados que son mostrados en la tabla de inicio de una seccion en los templates

    url_editar(self)
        Función que permite la edición de un registro de la tabla que se muestra al inicio de una sección en los templates

    url_borrar(self)
        Función que permite borrar un registro de la tabla que se muestra al inicio de una sección en los templates 

    """
    otra_operacion = models.CharField(max_length=255, blank=True)
    otro_bien_mueble = models.CharField(max_length=255, blank=True)
    marca = models.CharField(max_length=255, blank=True)
    modelo = models.CharField(max_length=255, blank=True)
    forma_pago = models.CharField(max_length=255, blank=True, choices=FORMAS_PAGO)
    anio = models.IntegerField(blank=True, null=True)
    num_serie = models.CharField(max_length=255, blank=True)
    otro_titular = models.CharField(max_length=255, blank=True)
    descripcion_bien = models.CharField(max_length=255, blank=True)
    otro_titular = models.CharField(max_length=255, blank=True)
    otra_forma = models.CharField(max_length=255, blank=True)
    fecha_adquisicion = models.DateField(null=True, blank=True)
    precio_adquisicion = models.IntegerField(null=True, blank=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tipo_relacion = models.ForeignKey(CatTiposRelacionesPersonales, on_delete=models.DO_NOTHING, blank=True, null=True)
    cat_paises = models.ForeignKey(CatPaises, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_formas_adquisiciones = models.ForeignKey(CatFormasAdquisiciones, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_monedas = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_muebles = models.ForeignKey(CatTiposMuebles, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_operaciones = models.ForeignKey(CatTiposOperaciones, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_titulares = models.ForeignKey(CatTiposTitulares, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_motivo_baja = models.ForeignKey(CatMotivoBaja, on_delete=models.DO_NOTHING, null=True, blank=True)
    domicilios = models.ForeignKey(Domicilios, on_delete=models.DO_NOTHING, blank=True, null=True)
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING)
    activos_bienes = models.ForeignKey(ActivosBienes, on_delete=models.DO_NOTHING)
    
    def declarante(self):
        try:
            return [BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.DECLARANTE).first().info_personal_var]
        except Exception as e:
            return None

    def copropietario(self):
        try:
            return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.COPROPIETARIO)
        except Exception as e:
            return None

    def propietario_anterior(self):
        try:
            return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.PROPIETARIO_ANTERIOR)
        except Exception as e:
            return None

    def observacion(self):
        return [self.observaciones]

    def columna_uno(self):
        if self.cat_tipos_operaciones:
            return u"{}".format(self.cat_tipos_operaciones)
        else:
            return u""

    def columna_dos(self):
        if self.cat_formas_adquisiciones:
            return u"{}".format(self.cat_formas_adquisiciones)
        else:
            return u""

    def columna_tres(self):
        if self.cat_tipos_titulares:
            return u"{}".format(self.cat_tipos_titulares)
        else:
            return u""

    def url_editar(self):
        return reverse_lazy('declaracion:muebles-noregistrables-editar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_borrar(self):
        return reverse_lazy('declaracion:muebles-noregistrables-borrar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_todos(self):
        return reverse_lazy('declaracion:muebles-noregistrables',
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

    def tipo_mueble(self):
        try:
            if self.cat_tipos_muebles.default:
                return u"{} {}".format(self.cat_tipos_muebles,
                                       self.otro_bien_mueble)
            else:
                return u"{}".format(self.cat_tipos_muebles)
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

    def forma_adquisicion(self):
        try:
            if self.cat_formas_adquisiciones.default:
                return u"{} {}".format(self.cat_formas_adquisiciones,
                                       self.otra_forma)
            else:
                return u"{}".format(self.cat_formas_adquisiciones)
        except Exception as e:
            return u""


class Inversiones(models.Model):
    """
    Class Modelo que guarda información de las inversiones del declarante
    
    Methods
    -------------
    coopropetario(self)
        Obtiene el primer registro de InfoPersonalVar donde el tipo de persona sea igual 12(Id correspindiente a CatTipoPersona)

    columna_uno(self),columna_dos(self) y columna(self)
        Obtienen los campos de registros ya guardados que son mostrados en la tabla de inicio de una seccion en los templates

    url_editar(self)
        Función que permite la edición de un registro de la tabla que se muestra al inicio de una sección en los templates

    url_borrar(self)
        Función que permite borrar un registro de la tabla que se muestra al inicio de una sección en los templates
    """
    otra_operacion = models.CharField(max_length=255, blank=True)
    otra_inversion = models.CharField(max_length=255, blank=True)
    otro_tipo_especifico = models.CharField(max_length=255, blank=True)
    num_cuenta = models.CharField(max_length=255, blank=True)
    rfc = models.CharField(max_length=255, blank=True)#/AGREGADO
    institucion = models.CharField(max_length=255, blank=True)#/AGREGADO
    otra_forma = models.CharField(max_length=255, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    monto_original = models.IntegerField(null=True, blank=True,default=0)
    tasa_interes = models.IntegerField(null=True, blank=True,default=0)
    saldo_actual = models.IntegerField(null=True, blank=True,default=0)
    plazo = models.IntegerField(null=True, blank=True, default=0)
    cat_tipos_titulares = models.ForeignKey(CatTiposTitulares, on_delete=models.DO_NOTHING, null=True, blank=True)
    otro_tipo_titular = models.CharField(max_length=255, blank=True)
    porcentaje_inversion = models.IntegerField(null=True, blank=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cat_formas_adquisiciones = models.ForeignKey(CatFormasAdquisiciones, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_monedas = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_paises = models.ForeignKey(CatPaises, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_especificos_inversiones = models.ForeignKey(CatTiposEspecificosInversiones, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_inversiones = models.ForeignKey(CatTiposInversiones, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_operaciones = models.ForeignKey(CatTiposOperaciones, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipo_persona = models.ForeignKey(CatTipoPersona, on_delete=models.DO_NOTHING, null=True, blank=True)
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING)
    info_personal_var = models.ForeignKey(InfoPersonalVar, on_delete=models.DO_NOTHING)
    cat_unidades_temporales = models.ForeignKey(CatUnidadesTemporales, on_delete=models.DO_NOTHING, null=True, blank=True)
    fondo_inversion = models.CharField(max_length=255, null=True, blank=True,choices=FONDOS_INVERSION)
    organizaciones = models.CharField(max_length=255, null=True, blank=True,choices=ORGANIZACIONES)
    posesiones = models.CharField(max_length=255, null=True, blank=True,choices=POSESIONES)
    seguros = models.CharField(max_length=255, null=True, blank=True,choices=SEGUROS)
    valores_bursatiles = models.CharField(max_length=255, null=True, blank=True,choices=VALORES)
    afores = models.CharField(max_length=255, null=True, blank=True,choices=AFORES)
    activos_bienes = models.ForeignKey(ActivosBienes, on_delete=models.DO_NOTHING, blank=True, null=True)

    def copropietario(self):
        try:
            return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes, cat_tipo_participacion_id=BienesPersonas.COPROPIETARIO)
        except Exception as e:
            return None

    def observacion(self):
        return [self.observaciones]

    def columna_uno(self):
        if self.cat_tipos_operaciones:
            return u"{}".format(self.cat_tipos_operaciones)
        else:
            return u""

    def columna_dos(self):
        if self.cat_tipos_inversiones:
            return u"{}".format(self.cat_tipos_inversiones)
        else:
            return u""

    def columna_tres(self):
        if self.cat_tipos_titulares:
            return u"{}".format(self.cat_tipos_titulares)
        else:
            return u""

    def url_editar(self):
        return reverse_lazy('declaracion:inversiones-editar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_borrar(self):
        return reverse_lazy('declaracion:inversiones-borrar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_todos(self):
        return reverse_lazy('declaracion:inversiones',
                            kwargs={'folio': self.declaraciones.folio})

    def persona(self):
        return [self.info_personal_var]

    def tipo_operacion(self):
        try:
            if self.cat_tipos_operaciones.default:
                return u"{} {}".format(self.cat_tipos_operaciones,
                                       self.otra_operacion)
            else:
                return u"{}".format(self.cat_tipos_operaciones)
        except Exception as e:
            return u""

    def titular(self):
        try:
            if self.cat_tipos_titulares.default:
                return u"{} {}".format(self.cat_tipos_titulares,
                                       self.otro_tipo_titular)
            else:
                return u"{}".format(self.cat_tipos_titulares)
        except Exception as e:
            return u""

    def forma_adquisicion(self):
        try:
            if self.cat_formas_adquisiciones.default:
                return u"{} {}".format(self.cat_formas_adquisiciones,
                                       self.otra_forma)
            else:
                return u"{}".format(self.cat_formas_adquisiciones)
        except Exception as e:
            return u""

    def tipo_inversion(self):
        try:
            if self.cat_tipos_inversiones.default:
                return u"{} {}".format(self.cat_tipos_inversiones,
                                       self.otra_inversion)
            else:
                return u"{}".format(self.cat_tipos_inversiones)
        except Exception as e:
            return u""

    def tipo_especifico(self):
        try:
            if self.cat_tipos_especificos_inversiones.default:
                return u"{} {}".format(self.cat_tipos_especificos_inversiones,
                                       self.otro_tipo_especifico)
            else:
                return u"{}".format(self.cat_tipos_especificos_inversiones)
        except Exception as e:
            return u""


class Fideicomisos(models.Model):
    """
    Class Modelo que guarda información de los fideicomisos del decclarante

    Methods
    -------------
    fideicomitente(self)
        Obtiene la información de fideicomitente por medio del campo de activos_bienes al modelo Bienes personas validando que el tipo de participación se FIDEICOMITENTE

    fideicomisario(self)
        Obtiene la información de fideicomisario por medio del campo de activos_bienes al modelo Bienes personas validando que el tipo de participación se FIDEICOMISARIO

    fiduciario(self)
        Obtiene la información de fiduciario por medio del campo de activos_bienes al modelo Bienes personas validando que el tipo de participación se FIDUCIARIO

    columna_uno(self),columna_dos(self) y columna(self)
        Obtienen los campos de registros ya guardados que son mostrados en la tabla de inicio de una seccion en los templates

    url_editar(self)
        Función que permite la edición de un registro de la tabla que se muestra al inicio de una sección en los templates

    url_borrar(self)
        Función que permite borrar un registro de la tabla que se muestra al inicio de una sección en los templates        

    """
    nombre_fideicomiso = models.CharField(max_length=255, blank=True)
    rfc = models.CharField(max_length=255, blank=True)#/AGREGADO
    tipo_persona = models.ForeignKey(CatTipoPersona, on_delete=models.DO_NOTHING, null=True, blank=True)#AGREGADO
    tipo_relacion = models.ForeignKey(CatTiposRelacionesPersonales, on_delete=models.DO_NOTHING, null=True, blank=True)#AGREGADO
    otra_operacion = models.CharField(max_length=255, blank=True)
    otro_fideicomiso = models.CharField(max_length=255, blank=True)
    objetivo_fideicomiso = models.CharField(max_length=255, blank=True)
    num_registro = models.CharField(max_length=255, blank=True)
    fecha_creacion = models.DateField(null=True, blank=True)
    plazo_vigencia = models.CharField(max_length=255, blank=True)
    valor_fideicomiso = models.IntegerField(null=True, blank=True,default=0)
    ingreso_monetario = models.IntegerField(null=True, blank=True,default=0)
    porcentaje = models.IntegerField(null=True, blank=True,default=0)
    institucion_fiduciaria = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cat_monedas = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_paises = models.ForeignKey(CatPaises, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_sectores_industria = models.ForeignKey(CatSectoresIndustria, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_fideicomisos = models.ForeignKey(CatTiposFideicomisos, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipos_operaciones = models.ForeignKey(CatTiposOperaciones, on_delete=models.DO_NOTHING, null=True, blank=True)
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING)
    activos_bienes = models.ForeignKey(ActivosBienes, on_delete=models.DO_NOTHING)
    cat_tipo_participacion = models.ForeignKey(CatTipoParticipacion, on_delete=models.DO_NOTHING, null=True, blank=True)

    def fideicomitente(self):
        try:
            return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.FIDEICOMITENTE).first()
        except Exception as e:
            return None

    def fideicomisario(self):
        try:
            return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.FIDEICOMISARIO).first()
            #return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,info_personal_var__cat_tipos_personas=InfoPersonalVar.TIPO_FIDEICOMISARIO).first()
        except Exception as e:
            return None

    def fiduciario(self):
        try:
            return BienesPersonas.objects.filter(activos_bienes = self.activos_bienes,cat_tipo_participacion_id=BienesPersonas.FIDUCIARIO).first()
        except Exception as e:
            return None

    def observacion(self):
        return [self.observaciones]
    def porcentajes(self):
        try:
            return [BienesPersonas.objects.filter(
                activos_bienes=self.activos_bienes,
                cat_tipo_participacion_id=BienesPersonas.DECLARANTE,
            ).first().porcentaje]
        except:
            None

    def columna_uno(self):
        if self.cat_tipos_operaciones:
            return u"{}".format(self.cat_tipos_operaciones)
        else:
            return u""

    def columna_dos(self):
        if self.cat_tipos_fideicomisos:
            return u"{}".format(self.cat_tipos_fideicomisos)
        else:
            return u""

    def columna_tres(self):
        if self.cat_sectores_industria:
            return u"{}".format(self.cat_sectores_industria)
        else:
            return u""

    def url_editar(self):
        return reverse_lazy('declaracion:fideicomisos-editar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_borrar(self):
        return reverse_lazy('declaracion:fideicomisos-borrar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_todos(self):
        return reverse_lazy('declaracion:fideicomisos',
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

    def tipo_fideicomiso(self):
        try:
            if self.cat_tipos_fideicomisos.default:
                return u"{} {}".format(self.cat_tipos_fideicomisos,
                                       self.otro_fideicomiso)
            else:
                return u"{}".format(self.cat_tipos_fideicomisos)
        except Exception as e:
            return u""
