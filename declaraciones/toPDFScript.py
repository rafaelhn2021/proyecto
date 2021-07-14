import os
import django
import uuid
import datetime
import sys
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration 
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.template.loader import render_to_string
import subprocess
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import redis
import time


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'declaraciones.settings')
django.setup()

from declaracion.models import Declaraciones, DeclaracionFiscal
from declaracion.views.confirmacion import (get_context_InformacionPersonal,get_context_Intereses,get_context_pasivos,
                                            get_context_ingresos, get_context_activos, get_context_vehiculos,
                                            get_context_inversiones,get_context_deudasotros,get_context_prestamocomodato,
                                            get_context_fideicomisos)
from declaracion.views.utils import (validar_declaracion, campos_configuracion_todos, declaracion_datos,set_declaracion_extendida_simplificada)
from django.contrib.auth.models import User
print("Ejecutando Script.....4b18dc8a-e228-4af0-9697-905a28ecb198-------GAER010101300")


def toPDF(args):
    context = {}
    declaracion_int = int(args[1])
    redis_cnx = redis.Redis(host='192.168.156.3',db=1,port=6379)
    redis_cnx.hmset("declaracion", {declaracion_int:0})

    declaracion = Declaraciones.objects.filter(pk=declaracion_int).first()

    context.update(get_context_InformacionPersonal(declaracion))
    context.update(get_context_Intereses(declaracion))
    context.update(get_context_ingresos(declaracion))
    context.update(get_context_activos(declaracion))

    #10% Del proceso ---------------------------------
    redis_cnx.hmset("declaracion",{declaracion_int:10})

    context.update({"vehiculos": get_context_vehiculos(declaracion)})
    context.update({"inversiones": get_context_inversiones(declaracion)})
    context.update({"adeudos": get_context_deudasotros(declaracion)})
    context.update({"prestamos": get_context_prestamocomodato(declaracion)})
    context.update({"fideicomisos": get_context_fideicomisos(declaracion)})
    context.update({"fiscal": DeclaracionFiscal.objects.filter(declaraciones=declaracion.pk).first()})
    context.update({"valor_privado_texto": "VALOR PRIVADO"})

    if declaracion.datos_publicos == False:
            context.update({"campos_privados": campos_configuracion_todos('p')})

    context.update(set_declaracion_extendida_simplificada(context['info_personal_fija']))

    #20% Del proceso ---------------------------------
    redis_cnx.hmset("declaracion",{declaracion_int:20})
    print('Consulta terminada----------------------------------------')

    template_name = "sitio/descargar.html"
    usuario_ = User.objects.get(pk=declaracion.info_personal_fija.usuario.pk)
    filename = "{}_{}_{}.pdf".format(usuario_.username,declaracion.cat_tipos_declaracion.codigo, declaracion.fecha_recepcion.date().strftime('%d%m%y'))

    #30% Del proceso ---------------------------------
    redis_cnx.hmset("declaracion",{declaracion_int:30})

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "inline; {}".format(filename)
    html = render_to_string(template_name, context)

    #40% Del proceso ---------------------------------
    redis_cnx.hmset("declaracion",{declaracion_int:40})
    print('PDF nombre de archivo----------------------------------------')
    year=datetime.date.today().year
    tipo=declaracion.cat_tipos_declaracion.codigo
    if context['info_personal_fija']:
        if context['info_personal_fija'].cat_puestos:
            area = context['info_personal_fija'].cat_puestos.cat_areas.codigo
        else: 
            area=""
    else: 
        area=""
    
    #50% Del proceso ---------------------------------
    redis_cnx.hmset("declaracion",{declaracion_int:50})

    directory = './media/declaraciones/'+tipo+'/'+str(year)+'/'+area+'/'
    file_path = os.path.join(directory, filename)

    if not os.path.exists(directory):
        os.makedirs(directory)

    #60% Del proceso ---------------------------------
    redis_cnx.hmset("declaracion",{declaracion_int:60})
    print('Creación de carpeta----------------------------------------')

    font_config = FontConfiguration()
    pdf2 = HTML(string=html,base_url=args[2]).write_pdf(font_config=font_config) #Convierte html a pdf para descargarse
    
    #70% Del proceso ---------------------------------
    redis_cnx.hmset("declaracion",{declaracion_int:70})
    print('PDF conversión de HTML ---------------------------------------------')
    f = open(file_path, "wb")
    
    #80% Del proceso ---------------------------------
    redis_cnx.hmset("declaracion",{declaracion_int:80})
    print("Abrir archivo ---------------------------------")
    f.write(pdf2)
    
    #90% Del proceso ---------------------------------
    redis_cnx.hmset("declaracion",{declaracion_int:90})
    print("Se guarda el html texto en pdf-----------------------------------------")
    f.close()
    print('Archivo creado----------------------------------------')

    #100% Del proceso ---------------------------------
    redis_cnx.hmset("declaracion",{declaracion_int:100})
    print("Proceso terminado ----------------------------------")

if __name__ == "__main__":
    toPDF(sys.argv)


