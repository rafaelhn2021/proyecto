import uuid
from django import template
from django.urls import resolve
from declaracion.models import (Secciones, SeccionDeclaracion, Declaraciones)
from declaracion.views.utils import (get_declaracion_anterior)
from api.serialize_functions import SECCIONES

register = template.Library()

@register.simple_tag(takes_context=True)
def no_aplica(context, folio=None, current_url=None, tipo=None):
    """
    Function no_aplica permite avanzar en la declaración si alguna de las secciones no aplica para el usuario
    """
    declaracion = None

    if current_url == None and tipo == None:
        request = context['request']
        current_url = resolve(request.path_info).url_name
        parametro = resolve(request.path_info).kwargs

        try:
            tipo = parametro['tipo']
        except Exception as e:
            tipo = None

        try:
            folio = uuid.UUID(context['folio_declaracion'])
        except Exception as e:
            folio = None
        
        try:
            declaracion = Declaraciones.objects.filter(folio=folio).first()
        except Exception as e:
            declaracion = None

    if tipo:
        seccion_id = Secciones.objects.filter(url=current_url,
                                              parametro=tipo).first()
    else:
        seccion_id = Secciones.objects.filter(url=current_url).first()

    if seccion_id:
        seccion = SeccionDeclaracion.objects.filter(
            declaraciones__folio=folio,
            seccion=seccion_id,
        ).first()

        if seccion:
            return not seccion.aplica
        else:
            #Asigna el valor de "aplica" de la sección de la declaración anterior cuando es guardada por primera vez
            try:
                if declaracion.cat_tipos_declaracion.codigo != 'INICIAL':
                    declaracion = get_declaracion_anterior(declaracion)
                    seccion_anterior = SeccionDeclaracion.objects.get(declaraciones=declaracion, seccion=seccion_id)

                    return not seccion_anterior.aplica
            except:
                 pass
                
            return False
