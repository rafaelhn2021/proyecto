from django.db import models
from django.urls import reverse_lazy
from .informacion_personal import(Declaraciones, Observaciones,
                                  InfoPersonalVar)
from .catalogos import (CatEntesPublicos, CatMonedas, CatTiposActividad,
                        CatTiposIngresosVarios, CatTiposMuebles, CatTiposInstrumentos,CatTiposBienes)
import locale


class IngresosDeclaracion(models.Model):
    """ 
    Class Modelo IngresosDeclaracion guardará información de los ingresos de la declaración
    -------
    Los registros de sección ingresos netos del declarante, pareja y/o dependientes y sección te desempeñaste como servidor público? son guardados en este modelo
    y se diferencian por el campo tipo_ingreso
                                  1=Ingreso declarante
                                  0=Ingreso servidor público

    """
    DEFAULT_MONEDA_ID = 101
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    declaraciones = models.ForeignKey(Declaraciones, on_delete=models.DO_NOTHING)
    ingreso_mensual_cargo = models.IntegerField(null=True, blank=True)
    cat_moneda_cargo = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, blank=True, related_name='cat_moneda_cargo',default=DEFAULT_MONEDA_ID)
    ingreso_mensual_otros_ingresos = models.IntegerField(null=True, blank=True)
    cat_moneda_otro_ingresos_mensual = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, blank=True, related_name='cat_moneda_otro_ingresos_mensual',default=DEFAULT_MONEDA_ID)
    ingreso_mensual_actividad = models.IntegerField(null=True, blank=True)
    cat_moneda_actividad = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, blank=True, related_name='cat_moneda_actividad',default=DEFAULT_MONEDA_ID)
    razon_social_negocio = models.CharField(max_length=100, blank=True, null=True)
    tipo_negocio = models.CharField(max_length=300, blank=True, null=True)
    ingreso_mensual_financiera = models.IntegerField(null=True, blank=True)
    cat_moneda_financiera = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, blank=True, related_name='cat_moneda_financiera',default=DEFAULT_MONEDA_ID)
    cat_tipo_instrumento = models.ForeignKey(CatTiposInstrumentos, on_delete=models.DO_NOTHING, blank=True, null=True)
    otro_tipo_instrumento = models.CharField(max_length=255, blank=True)
    ingreso_mensual_servicios = models.IntegerField(null=True, blank=True)
    cat_moneda_servicios = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, blank=True, related_name='cat_moneda_servicios',default=DEFAULT_MONEDA_ID)
    tipo_servicio = models.CharField(max_length=100, blank=True, null=True)
    ingreso_otros_ingresos= models.IntegerField(null=True, blank=True)
    cat_moneda_otros_ingresos = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, blank=True, related_name='cat_moneda_otros_ingresos',default=DEFAULT_MONEDA_ID)
    cat_tipos_actividad = models.ForeignKey(CatTiposActividad, on_delete=models.DO_NOTHING, blank=True, null=True)
    ingreso_mensual_neto = models.IntegerField(null=True, blank=True)
    cat_moneda_neto = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, blank=True, related_name='cat_moneda_neto',default=DEFAULT_MONEDA_ID)
    ingreso_mensual_pareja_dependientes = models.IntegerField(null=True, blank=True)
    cat_moneda_pareja_dependientes = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, blank=True, related_name='cat_moneda_pareja_dependientes',default=DEFAULT_MONEDA_ID)
    ingreso_mensual_total = models.IntegerField(null=True, blank=True)
    cat_moneda_total = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, blank=True, related_name='cat_moneda_total',default=DEFAULT_MONEDA_ID)
    observaciones = models.ForeignKey(Observaciones, on_delete=models.DO_NOTHING,blank=True)

    ingreso_anio_anterior = models.BooleanField(blank=True, null=True, default=False)
    ingreso_enajenacion_bienes = models.IntegerField(null=True, blank=True)
    cat_moneda_enajenacion_bienes = models.ForeignKey(CatMonedas, on_delete=models.DO_NOTHING, blank=True, related_name='cat_moneda_enajenacion_bienes',default=DEFAULT_MONEDA_ID)
    fecha_ingreso = models.DateField(blank=True, null=True)
    fecha_conclusion = models.DateField(blank=True, null=True) 
    cat_tipos_bienes = models.ForeignKey(CatTiposBienes,on_delete=models.DO_NOTHING, blank=True, null=True)
    tipo_ingreso = models.BooleanField(blank=True, null=True)