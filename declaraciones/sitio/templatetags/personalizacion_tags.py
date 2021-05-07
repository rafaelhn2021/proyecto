from django import template
from sitio.models import sitio_personalizacion

register = template.Library()

@register.simple_tag(name='personalizacion')
def personalizacion(opcion):
    try:
        obj = sitio_personalizacion.objects.filter(id=1).values()[0]
        result = obj[opcion]
    except Exception as e:
        return "Sin Nombrar" + str(e)
    return result



