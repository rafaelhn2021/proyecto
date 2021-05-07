import datetime
from django import template
from declaracion.models import (Secciones)

register = template.Library()

@register.simple_tag
def current_time():
    """
    Function current_time obtiene las secciones padres de la declaración
    """
    secciones = Secciones.objects.filter(level=0)
    return secciones

@register.simple_tag
def get_status(seccion, folio):
    """
    Function get_status obtiene el estatus de una declaración
    """
    seccion = Secciones.objects.get(id=seccion.id)
    status = seccion.get_status(folio)
    return status

@register.simple_tag
def show_menu(path, seccion):
    """
    Function show_menu retorna nombre de la clase css para mostrar un estilo diferente a aquellas secciones padre
    """
    if "declaracion/informacion-personal" in path and "DECLARACIÓN PATRIMONIAL" in seccion:
        return 'show'
    elif "declaracion/intereses" in path and "DECLARACION DE INTERESES" in seccion:        
        return 'show'
    elif "/declaracion/ingresos" in path and "DECLARACIÓN PATRIMONIAL" in seccion:        
        return 'show'
    elif "/declaracion/activos" in path and "DECLARACIÓN PATRIMONIAL" in seccion:        
        return 'show'
    elif "/declaracion/pasivos" in path and "DECLARACIÓN PATRIMONIAL" in seccion:        
        return 'show'   
    else:
        return path + seccion
    
