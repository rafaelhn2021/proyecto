import uuid
import os
from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE
from django.urls import reverse_lazy
from smart_selects.db_fields import ChainedForeignKey

from .catalogos import (CatPaises, CatEstadosCiviles,
                        CatTiposDeclaracion, CatRegimenesMatrimoniales,
                        CatGradosAcademicos, CatEstatusEstudios,
                        CatDocumentosObtenidos, CatEntesPublicos,
                        CatOrdenesGobierno,CatSectoresIndustria,
                        CatFuncionesPrincipales, CatAmbitosLaborales,
                        CatTiposRelacionesPersonales, CatPoderes,
                        CatTipoPersona, CatEntidadesFederativas, CatTipoVia,
                        CatMunicipios, CatMonedas,CatTiposOperaciones,CatEstatusDeclaracion,CatPuestos)
from django.db.models.signals import post_delete
from django.dispatch import receiver

#Se agrego variable global para los campos de modelos que lo necesiten ya que la informaciòn es la misma
TIPO_OPERACION = [
    ('AGREGAR', 'Agregar'),
    ('MODIFICAR', 'Modificar'),
    ('SIN_CAMBIO', 'Sin cambio'),
    ('BAJA', 'Baja')
]


class InfoPersonalFija(models.Model):
    """
    En este modelo se guarda la información personal del declarante
    """
    nombres = models.CharField(max_length=255, blank=True)
    apellido1 = models.CharField(max_length=255, blank=True, verbose_name="Apellido Paterno")
    apellido2 = models.CharField(max_length=255, blank=True, verbose_name="Apellido Materno")
    curp = models.CharField(max_length=255, blank=True)
    puesto = models.CharField(max_length=255, blank=True, null=True)
    cat_puestos = models.ForeignKey(CatPuestos, on_delete=models.DO_NOTHING, blank=True, null=True,verbose_name="Puesto") # AGREGADO 10/03/21 GG
    rfc = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=14, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    cat_ente_publico = models.ForeignKey(CatEntesPublicos, on_delete=models.DO_NOTHING, blank=True, null=True)
    cat_entidades_federativas = models.ForeignKey(CatEntidadesFederativas, on_delete=models.DO_NOTHING, null=True, blank=True)
    nombre_ente_publico = models.CharField(max_length=300, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    cat_pais = models.ForeignKey(CatPaises, on_delete=models.DO_NOTHING, null=True, blank=True)
    otro_ente = models.CharField(max_length=255, blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    sended = models.BooleanField(blank=True, null=True, default=False)

    def nombre_completo(self):
        return u"{} {} {}".format(self.nombres, self.apellido1,self.apellido2)



class Declaraciones(models.Model):
    """
    Modelo que guarda información de la declaración
    """
    folio = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    fecha_recepcion = models.DateTimeField(blank=True, null=True)
    fecha_declaracion = models.DateField(null=True, auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cat_tipos_declaracion = models.ForeignKey(CatTiposDeclaracion, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_estatus = models.ForeignKey(CatEstatusDeclaracion, on_delete=models.DO_NOTHING, default=1)
    avance = models.IntegerField(blank=True,default=0)
    info_personal_fija = models.ForeignKey(InfoPersonalFija, on_delete=models.DO_NOTHING)
    extemporanea = models.BooleanField(blank=True, null=True, default=0)
    datos_publicos = models.BooleanField(blank=True, null=True, default=0)


class Domicilios(models.Model):
    """
    Modelo que guarda información de los domicilios
    ---------
    Debido a que existen multiples personas relacionadas que se crearán en la declaración 
    muchas contarán con direcciones propias(ej. Dependientes economicos)
    """
    cp = models.CharField(max_length=255, blank=True)
    colonia = models.CharField(max_length=255, blank=True)
    nombre_via = models.CharField(max_length=255, blank=True)
    num_exterior = models.CharField(max_length=255, blank=True)
    num_interior = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cat_entidades_federativas = models.ForeignKey(CatEntidadesFederativas, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_pais = models.ForeignKey(CatPaises, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_tipo_via = models.ForeignKey(CatTipoVia, on_delete=models.DO_NOTHING, null=True, blank=True)
    municipio = models.ForeignKey(CatMunicipios, on_delete=models.DO_NOTHING,blank=True, null=True)
    ciudadLocalidad = models.CharField(max_length=100, blank=True, null=True)
    estadoProvincia = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering=('pk',)

    def __str__(self):
        try: 
            return self.nombre_via + self.num_exterior + self.num_interior + self.colonia + self.cp  
        except:
            return "Domicilio"


class Observaciones(models.Model):
    """
    Modelo que guarda las observaciones por secciones
    """
    observacion = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.observacion


class InfoPersonalVar(models.Model):
    """
    Modelo que guarda información de multiples personas relacionadas a una declaración del declarante
    ---------
    Uso principal: Guarda información de
                                        -Pareja
                                        -Dependientes economicos
                                        -Empresa
                                        -Cliente
                                        -Etc, Más en el catálogo tipoPersona
    """
    TIPO_DECLARANTE = 1
    TIPO_DEPENDIENTE = 2
    TIPO_EMPRESA = 3
    TIPO_SOCIO = 4
    TIPO_CLIENTE = 5
    TIPO_SOCIEDAD = 6
    TIPO_INSTITUCION = 7
    TIPO_FIDEICOMISARIO = 8
    TIPO_FIDEICOMITENTE = 9
    TIPO_FIDUCIARIO = 10
    TIPO_COPROPIETARIO = 12
    TIPO_PROPIETARIO_ANTERIOR = 13
    TIPO_PRESTATARIO = 14
    es_fisica = models.BooleanField(blank=True, null=True, default=None)
    razon_social = models.CharField(max_length=255, blank=True, null=True)
    nombres = models.CharField(max_length=255, blank=True)
    apellido1 = models.CharField(max_length=255, blank=True)
    apellido2 = models.CharField(max_length=255, blank=True)
    curp = models.CharField(max_length=255, blank=True)
    rfc = models.CharField(max_length=255, blank=True)
    homoclave = models.CharField(max_length=3, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    num_id_identificacion = models.CharField(max_length=255, blank=True)
    email_personal = models.CharField(max_length=255, blank=True)
    tel_particular = models.CharField(max_length=255, blank=True)
    tel_movil = models.CharField(max_length=255, blank=True)
    cat_entidades_federativas = models.ForeignKey(CatEntidadesFederativas, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_estados_civiles = models.ForeignKey(CatEstadosCiviles, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_pais = models.ForeignKey(CatPaises, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_regimenes_matrimoniales = models.ForeignKey(CatRegimenesMatrimoniales, on_delete=models.DO_NOTHING, null=True, blank=True)
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING)
    domicilios = models.ForeignKey(Domicilios, on_delete=models.DO_NOTHING, blank=True, null=True)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING, blank=True, null=True)
    cat_tipo_persona = models.ForeignKey(CatTipoPersona, on_delete=models.DO_NOTHING, blank=True, null=True)
    cat_sectores_industria = models.ForeignKey(CatSectoresIndustria, on_delete=models.DO_NOTHING, blank=True, null=True)
    otro_sector = models.CharField(max_length=255, blank=True, null=True)
    otro_estado_civil = models.CharField(max_length=255, blank=True, null=True)
    actividad_economica = models.CharField(max_length=255, blank=True, null=True)
    ocupacion_girocomercial = models.CharField(max_length=255, blank=True, null=True)
    nombre_negocio = models.CharField(max_length=255, blank=True, null=True)
    rfc_negocio = models.CharField(max_length=50, blank=True, null=True) #/AGREGADO
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    nacionalidades = models.ManyToManyField(CatPaises, through='Nacionalidades', related_name="info_personal_var_nacionalidaes", blank=True)
    activos_bienes = models.ManyToManyField(
        'ActivosBienes',
        through='BienesPersonas',
        through_fields=('info_personal_var', 'activos_bienes'),
        related_name="info_personal_var_activos_bienes")


    class Meta:
        ordering=('pk',)

    def __str__(self):
        return self.rfc

    def nombre_completo(self):
        if self.es_fisica:
            return ("%s %s %s")%(self.nombres ,self.apellido1,self.apellido2)
        else:
            return self.razon_social

    def domicilio(self):
        return [self.domicilios]

    def observacion(self):
        return [self.observaciones]

    def nacionalidad(self):
        try:
            return self.nacionalidades.all()
        except:
            return None

    def tipo(self):
        return self.cat_tipo_persona_id

    def sectores_industrias(self):
        try:
            if self.cat_sectores_industria.default:
                return u"{} {}".format(self.cat_sectores_industria,
                                       self.otro_sector)
            else:
                return u"{}".format(self.cat_sectores_industria)
        except Exception as e:
            return u""


class Nacionalidades(models.Model):
    cat_paises = models.ForeignKey(CatPaises, models.DO_NOTHING, null=True, blank=True, related_name="nacionalidades_cat_paises")
    info_personal_var = models.ForeignKey(InfoPersonalVar, models.DO_NOTHING, related_name="nacionalidades_info_personal_var")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DatosCurriculares(models.Model):
    """ 
    Class Modelo DatosCurriculares guardará información curricular del declarante(educación)

    Methods
    ---------
    columna_uno(self),columna_dos(self) y columna(self)
        Obtienen los campos de registros ya guardados que son mostrados en la tabla de inicio de una seccion en los templates

    url_editar(self)
        Función que permite la edición de un registro de la tabla que se muestra al inicio de una sección en los templates

    url_borrar(self)
        Función que permite borrar un registro de la tabla que se muestra al inicio de una sección en los templates
    """
    institucion_educativa = models.CharField(max_length=255, blank=True)
    municipio = models.ForeignKey(CatMunicipios, on_delete=models.DO_NOTHING, null=True,blank=True)
    carrera_o_area = models.CharField(max_length=255, blank=True)
    conclusion = models.DateField(max_length=255, blank=True,null=True)
    cedula_profesional = models.CharField(max_length=255, blank=True)
    diploma = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cat_documentos_obtenidos = models.ForeignKey(CatDocumentosObtenidos, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_entidades_federativas = models.ForeignKey(CatEntidadesFederativas, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_estatus_estudios = models.ForeignKey(CatEstatusEstudios, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_grados_academicos = models.ForeignKey(CatGradosAcademicos, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_pais = models.ForeignKey(CatPaises, on_delete=models.DO_NOTHING, null=True, blank=True)
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING)
    cat_tipos_operaciones = models.ForeignKey(CatTiposOperaciones, on_delete=models.DO_NOTHING, null=True, blank=True)#/AGREGADO


    def columna_uno(self):
        if self.cat_grados_academicos:
            return u"{}".format(self.cat_grados_academicos)
        else:
            return u""

    def columna_dos(self):
        if self.institucion_educativa:
            return u"{}".format(self.institucion_educativa)
        else:
            return u""

    def columna_tres(self):
        if self.carrera_o_area:
            return u"{}".format(self.carrera_o_area)
        else:
            return u""

    def url_editar(self):
        return reverse_lazy('declaracion:datos-curriculares-editar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_borrar(self):
        return reverse_lazy('declaracion:datos-curriculares-borrar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_todos(self):
        return reverse_lazy('declaracion:datos-curriculares',
                            kwargs={'folio': self.declaraciones.folio})

    def observacion(self):
        return [self.observaciones]


class Encargos(models.Model):
    """ 
    Class Modelo Encargos guardará información del cargo asumido del declarante
    ---------
    Modelo también utilizado para guardar información del cargo que puede llegar a tener algún dependiente económico
    """
    empleo_cargo_comision = models.CharField(max_length=255, blank=True, null=True)
    honorarios = models.BooleanField(blank=True, null=True, default=False)
    nivel_encargo = models.CharField(max_length=255, blank=True, null=True)
    area_adscripcion = models.CharField(max_length=255, blank=True, null=True)
    posesion_conclusion = models.DateField(blank=True, null=True)
    posesion_inicio = models.DateField(blank=True, null=True)
    telefono_laboral = models.CharField(max_length=255, blank=True, null=True)
    email_laboral = models.CharField(max_length=255, blank=True, null=True)
    otro_sector = models.CharField(max_length=255, blank=True, null=True)
    otra_funcion = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cat_entes_publicos = models.ForeignKey(CatEntesPublicos, on_delete=models.DO_NOTHING, blank=True, null=True)
    cat_funciones_principales = models.ForeignKey(CatFuncionesPrincipales, on_delete=models.DO_NOTHING, blank=True, null=True)
    cat_ordenes_gobierno = models.ForeignKey(CatOrdenesGobierno, on_delete=models.DO_NOTHING, blank=True, null=True)
    cat_paises = models.ForeignKey(CatPaises, on_delete=models.DO_NOTHING, blank=True, null=True)
    cat_sectores_industria = models.ForeignKey(CatSectoresIndustria, on_delete=models.DO_NOTHING, blank=True, null=True)
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING, blank=True, null=True)#/MODIFICADO 27-01-20
    domicilios = models.ForeignKey(Domicilios, on_delete=models.DO_NOTHING,blank=True, null=True)#/MODIFICADO 27-01-20
    telefono_extension = models.CharField(max_length=255, blank=True, null=True)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING,blank=True, null=True)#/MODIFICADO 27-01-20
    otro_naturalezas_juridicas = models.CharField(max_length=255, blank=True, null=True)
    cat_poderes = models.ForeignKey(CatPoderes, on_delete=models.DO_NOTHING, blank=True, null=True)
    cat_tipos_operaciones = models.ForeignKey(CatTiposOperaciones, on_delete=models.DO_NOTHING, blank=True, null=True)#/AGREGADO
    otro_ente = models.CharField(max_length=255, blank=True, null=True)
    salarioMensualNeto = models.IntegerField(blank=True, null=True)
    rfc = models.CharField(max_length=255, blank=True, null=True) #/AGREGADO
    nombreEmpresaSociedadAsociacion = models.CharField(max_length=255, blank=True, null=True) #/AGREGADO
    moneda = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, blank=True, null=True)
    nombre_ente_publico = models.CharField(max_length=300, null=True, blank=True)
    cat_puestos = models.ForeignKey(CatPuestos, on_delete=models.SET_NULL, blank=True, null=True)#/AGREGADO 07-02-20 GG

    def observacion(self):
        return [self.observaciones]

    def poderes(self):
        try:
            if self.cat_poderes.default:
                return u"{} {}".format(self.cat_poderes, self.otro_naturalezas_juridicas)
            else:
                return u"{}".format(self.cat_poderes)
        except Exception as e:
            return u""


class ExperienciaLaboral(models.Model):
    """ 
    Class Modelo ExperienciaLaboral guardará información de antedecentes laborales del declarante

    Methods
    ---------
    columna_uno(self),columna_dos(self) y columna(self)
        Obtienen los campos de registros ya guardados que son mostrados en la tabla de inicio de una seccion en los templates

    url_editar(self)
        Función que permite la edición de un registro de la tabla que se muestra al inicio de una sección en los templates

    url_borrar(self)
        Función que permite borrar un registro de la tabla que se muestra al inicio de una sección en los templates
    """
    otro_poder = models.CharField(max_length=255, blank=True)
    nombre_institucion = models.CharField(max_length=255, blank=True)
    unidad_area_administrativa = models.CharField(max_length=255, blank=True)
    otro_sector = models.CharField(max_length=255, blank=True)
    jerarquia_rango = models.CharField(max_length=255, blank=True)
    cargo_puesto = models.CharField(max_length=255, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    fecha_salida = models.DateField(null=True, blank=True)
    otra_funcion = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cat_ambitos_laborales = models.ForeignKey(CatAmbitosLaborales, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_funciones_principales = models.ForeignKey(CatFuncionesPrincipales, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_ordenes_gobierno = models.ForeignKey(CatOrdenesGobierno, on_delete=models.DO_NOTHING, null=True, blank=True)
    cat_poderes = models.ForeignKey(CatPoderes, on_delete=models.DO_NOTHING, null=True, blank=True,default=1)
    cat_sectores_industria = models.ForeignKey(CatSectoresIndustria, on_delete=models.DO_NOTHING, null=True, blank=True)
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING)
    domicilios = models.ForeignKey(Domicilios, on_delete=models.DO_NOTHING)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING)
    otro_ambitos_laborales = models.CharField(max_length=255, blank=True)

    cat_tipos_operaciones = models.ForeignKey(CatTiposOperaciones, on_delete=models.DO_NOTHING, null=True, blank=True) #/AGREGADO
    rfc = models.CharField(max_length=255, blank=True) #/AGREGADO

    def columna_uno(self):
        if self.nombre_institucion:
            return u"{}".format(self.nombre_institucion)
        else:
            return u""

    def columna_dos(self):
        if self.cat_ambitos_laborales:
            return u"{}".format(self.cat_ambitos_laborales)
        else:
            return u""

    def columna_tres(self):
        if self.cargo_puesto:
            return u"{}".format(self.cargo_puesto)
        else:
            return u""

    def url_editar(self):
        return reverse_lazy('declaracion:experiencia-laboral-editar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_borrar(self):
        return reverse_lazy('declaracion:experiencia-laboral-borrar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_todos(self):
        return reverse_lazy('declaracion:experiencia-laboral',
                            kwargs={'folio': self.declaraciones.folio})

    def observacion(self):
        return [self.observaciones]

    def funciones_principales(self):
        try:
            if self.cat_funciones_principales.default:
                return u"{} {}".format(self.cat_funciones_principales,
                                       self.otra_funcion)
            else:
                return u"{}".format(self.cat_funciones_principales)
        except Exception as e:
            return u""

class ConyugeDependientes(models.Model):
    """
    Modelo que guarda informacioón de todos los dependientes económicos del declarante
    ---------
    Los registro de la paraja/conyugue y demás dependientes(hijo,madre,etc) son guardados aquí y se diferencian de acuerdo al campo es_pareja

    Methods
    ---------
    columna_uno(self),columna_dos(self) y columna(self)
       Obtienen los campos de registros ya guardados que son mostrados en la tabla de inicio de una seccion en los templates

    url_editar(self)
        Función que permite la edición de un registro de la tabla que se muestra al inicio de una sección en los templates

    url_borrar(self)
        Función que permite borrar un registro de la tabla que se muestra al inicio de una sección en los templates
    """
    medio_contacto = models.CharField(max_length=255, blank=True)
    habita_domicilio = models.BooleanField(blank=True, null=True, default=False)
    ingresos_propios = models.BooleanField(blank=True, null=True, default=False)
    ocupacion_profesion = models.CharField(max_length=255, blank=True)
    proveedor_contratista = models.BooleanField(blank=True, null=True, default=False)
    otro_sector = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cat_tipos_relaciones_personales = models.ForeignKey(CatTiposRelacionesPersonales, on_delete=models.DO_NOTHING, null=True, blank=True)
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING)
    otra_relacion = models.CharField(max_length=255, blank=True)
    otra_relacion_familiar = models.CharField(max_length=255, blank=True)
    declarante_infopersonalvar = models.ForeignKey(InfoPersonalVar, on_delete=models.DO_NOTHING, related_name="declarante_conyugue_dependientes")
    dependiente_infopersonalvar = models.ForeignKey(InfoPersonalVar, on_delete=models.DO_NOTHING, related_name="dependiente_conyugue_dependientes")
    actividadLaboral = models.ForeignKey(CatAmbitosLaborales, on_delete=models.DO_NOTHING, null=True, blank=True) #/AGREGADO
    otra_actividadLaboral = models.CharField(max_length=255, blank=True)#/AGRAGADO 30/08/20
    actividadLaboralSector = models.ForeignKey(Encargos, on_delete=models.DO_NOTHING, null=True, blank=True) #/AGREGADO
    cat_tipos_operaciones = models.ForeignKey(CatTiposOperaciones, on_delete=models.DO_NOTHING, null=True, blank=True) #/AGREGADO
    es_pareja = models.BooleanField(blank=True, null=True,default=True) #/AGREGADO 27/01/20
    es_extranjero = models.BooleanField(blank=True, null=True,default=True) #/AGREGADO 01/02/20

    def columna_uno(self):
        return u"{} {} {}".format(
            self.dependiente_infopersonalvar.nombres,
            self.dependiente_infopersonalvar.apellido1,
            self.dependiente_infopersonalvar.apellido2,
            )

    def columna_dos(self):
        if self.cat_tipos_relaciones_personales:
            return u"{}".format(self.cat_tipos_relaciones_personales)
        else:
            return u""

    def columna_tres(self):
        if self.actividadLaboral:
            return u"{}".format(self.actividadLaboral)
        else:
            return u""

    def url_editar(self):
        return reverse_lazy('declaracion:dependientes-economicos-editar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_borrar(self):
        return reverse_lazy('declaracion:dependientes-economicos-borrar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

    def url_todos(self):
        return reverse_lazy('declaracion:dependientes-economicos',
                            kwargs={'folio': self.declaraciones.folio})
    def observacion(self):

        return [self.observaciones]

    def dependiente(self):
        return [self.dependiente_infopersonalvar]

    def nacionalidad(self):
        return self.dependiente_infopersonalvar.nacionalidad()

    def domicilio(self):
        return [self.declarante_infopersonalvar.domicilios]

    def tipo_relacion_personal(self):
        try:
            if self.cat_tipos_relaciones_personales.default:
                return u"{} {}".format(self.cat_tipos_relaciones_personales,
                                  self.otra_relacion)
            else:
                return u"{}".format(self.cat_tipos_relaciones_personales)
        except Exception as e:
            return u""


class DeclaracionFiscal(models.Model):
    """
    Modelo que guarda principalmente archivo PDF

    Methods
    ---------
    columna_uno(self) y columna_dos(self)
        Obtienen los campos de registros ya guardados que son mostrados en la tabla de inicio de una seccion en los templates

    url_borrar(self)
        Función que permite borrar un registro de la tabla que se muestra al inicio de una sección en los templates
    """
    archivo_xml =  models.FileField(upload_to="declaracion_fiscal/xml", blank=True, null=True)
    archivo_pdf =  models.FileField(upload_to="declaracion_fiscal/pdf", blank=True, null=True)
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING, null=True, blank=True)

    def columna_uno(self):
        return u"{}".format(
            self.archivo_xml
        )

    def columna_dos(self):
        return u"{}".format(
            self.archivo_pdf
        )
    
    def filename(self):
        return os.path.basename(self.archivo_pdf.name)

    def url_borrar(self):
        return reverse_lazy('declaracion:declaracion-fiscal-borrar',
                            kwargs={'folio': self.declaraciones.folio,
                                    'pk': self.id})

@receiver(post_delete, sender=DeclaracionFiscal)
def submission_delete(sender, instance,**kwargs):
    try:
        instance.archivo_pdf.delete(False)
    except Exception as e:
        print('Exception----------------->',e)
