import traceback
import uuid
import sys
import datetime
from django.urls import resolve
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from declaracion.forms import BienesPersonasForm
from declaracion.models import (Declaraciones, Secciones, SeccionDeclaracion, CatCamposObligatorios, Domicilios,
                                BienesInmuebles, BienesMuebles, MueblesNoRegistrables, Fideicomisos,
                                BienesPersonas, InfoPersonalVar, Apoyos, ConyugeDependientes,
                                Observaciones, InfoPersonalFija)
from declaracion.models.catalogos import CatPuestos
from django.apps import apps
from django.conf import settings



def validar_declaracion(request, folio_declaracion):
    """Obtiene información de la declaración por folio y usuario"""
    declaracion = Declaraciones.objects.filter(
        folio = uuid.UUID(folio_declaracion),
        info_personal_fija__usuario = request.user,
        cat_estatus__pk__in = (1, 2, 3)
        ).first()
    if declaracion:
        return declaracion
    else:
        raise ObjectDoesNotExist


def campos_configuracion(seccion="", tipo=""):
    """
    Función que obtiene información sobre los campos de una sección especifica
    Uso principal: Realizar conteo de aquellos campos obligatorios por sección(Avance % de la declaración) y mostrar cuáles serán privados
    ...
    Parameters
    ----------
        seccion: QuerySet
            QuerySet de la sección
        tipo: str
            o=Obligatorio, p=Privado
    """
    campos = []
    filtro = Q(esta_pantalla=True)
    if seccion:
        filtro &= Q(seccion_id=seccion.id)
        if tipo=='p':
           filtro&= Q(es_privado=True)
        else:
           filtro&= Q(es_obligatorio=True)

    c_config = CatCamposObligatorios.objects.filter(filtro)
    for campo in c_config:
        columa = campo.nombre_columna.replace("_id","")
        campos.append(columa)
    return campos


def campos_configuracion_todos(tipo=""):
    """
    Función que obtiene información sobre los campos de todas las secciones de la declaración
    Uso principal: Mostrar información en 'Firmar mi declaración'
    ...
    Parametros
    ----------
        tipo: str
            o=Obligatorio, p=Privado
    """
    campos = []
    filtro = Q(esta_pantalla=True)
    if tipo=='p':
        filtro&= Q(es_privado=True)
    else:
        filtro&= Q(es_obligatorio=True)

    c_config = CatCamposObligatorios.objects.filter(filtro)
    for campo in c_config:
        nombre = campo.nombre_columna.replace("_id","")
        url = campo.seccion.url
        columna = "{}-{}".format(url,nombre)
        campos.append(columna)
    return campos

def actualizar_aplcia(modelo, declaracion, id_seccion):
    aplica=1
    try:
        m = modelo.objects.filter(declaraciones=declaracion).first()
        seccion_dec = SeccionDeclaracion.objects.filter(declaraciones=declaracion, seccion=Secciones.objects.get(pk=id_seccion))
    except Exception as e:
        print(e)

    if m:
        aplica=0


    if m is None and seccion_dec.exists():
        seccion_d = seccion_dec.first()
        if seccion_d.aplica == 1:
            SeccionDeclaracion.objects.filter(declaraciones=declaracion, seccion=Secciones.objects.get(pk=id_seccion)).delete()

    return aplica


def declaracion_datos(kwargs, modelo, declaracion):
    """
    Función que obtiene datos guardados por modelo y delcaración
    ...
    Parametros
    ----------
        kwargs: str
            Permiten pasar argumentos como nombres de parámetros
        modelo:  modelo
            Modelo del cual se obtendrá la información
        declaracion: class
           Información de la declaración actual
    """
    agregar = kwargs.get("agregar", False)
    editar_id = kwargs.get("pk", False)
    tipo = kwargs.get("tipo", False)
    cat_tipos_pasivos = kwargs.get("cat_tipos_pasivos", False)
    es_representacion_activa = kwargs.get("es_representacion_activa", False)
    es_pareja = kwargs.get("es_pareja", False)
    beneficiario_infopersonalvar = kwargs.get("beneficiario_infopersonalvar", False)
    prestamocomodato = kwargs.get("prestamocomodato",False)

    q = Q(declaraciones=declaracion)

    if beneficiario_infopersonalvar:
        q &= Q(beneficiario_infopersonalvar=beneficiario_infopersonalvar)
    if 'es_representacion_activa' in kwargs:
        q &= Q(es_representacion_activa=es_representacion_activa)
    if cat_tipos_pasivos:
        q &= Q(cat_tipos_pasivos_id=int(cat_tipos_pasivos))
    if tipo:
        q &= Q(cat_tipos_ingresos_varios_id=int(tipo)+1)
    if 'es_pareja' in kwargs:
        q &= Q(es_pareja=es_pareja)
    if prestamocomodato:
        q &= Q(campo_default=False)

    if agregar:
        data = None
    elif editar_id:
        data = modelo.objects.filter(
            Q(pk=editar_id) & q
            ).first()
    else:
        data = modelo.objects.filter(q).last()

    data_todos = modelo.objects.filter(q)

    return agregar, editar_id, data, data_todos


def no_aplica(request):
    """ Función que retorna True o False determinado por el valor dado(no_aplica) """
    try:
        no_aplica = request.POST['no_aplica']
        no_aplica = True
    except KeyError:
        no_aplica = False

    return not no_aplica


def obtiene_rfc(rfc=""):
    """ Función que obtiene la fecha de nacimiento a partir del RFC """
    try:
        anio = rfc[4:6]
        mes = rfc[6:8]
        dia = rfc[8:10]

        year = datetime.date.today().year

        if int("20" + anio) > year:
            anio = int("19" + anio)
        else:
            anio = int("20" + anio)
        return u"{}-{}-{}".format(anio, mes, dia)
    except Exception as e:
        print (e)
        return ''


def guardar_estatus(request, folio, estatus, parametro=None, aplica=True, **kwargs):
    """ 
    Función que guarda la sección de la declaración 
    ....
    Parametros
    ----------
       request:
            Pasa el estado a través del sistema
        folio: str
            Folio de la declaración
        estatus: int
            Variable en el modelo de Secciones llamada COMPLETA=2
        aplica: bool
            Valor obtenido si el check mostrado en pantalla de la sección ha sido seleccionado o no
    """
    current_url = resolve(request.path_info).url_name

    if parametro:
        seccion_id = Secciones.objects.filter(url=current_url,
                                              parametro=parametro).first()
    else:
        seccion_id = Secciones.objects.filter(url=current_url).first()
    declaraciones = Declaraciones.objects.filter(folio=folio).first()
    try:
        seccion_dec_id = SeccionDeclaracion.objects.filter(declaraciones=declaraciones, seccion=seccion_id).first()
    except Exception as e:
        seccion_dec_id = None

    observaciones = None
    if "observaciones" in kwargs:
        observaciones = kwargs["observaciones"]

    if seccion_id:
        if seccion_dec_id:
            seccion_dec_id.aplica=aplica
            seccion_dec_id.estatus=estatus
            seccion_dec_id.observaciones=observaciones
            seccion_dec_id.save()
            obj=seccion_dec_id
            created=seccion_dec_id.pk
        else:
            obj, created = SeccionDeclaracion.objects.update_or_create(
                declaraciones=declaraciones,
                seccion=seccion_id,
                defaults={'aplica': aplica, 'estatus': estatus},
                observaciones=observaciones
            )
        try:
            obtiene_avance(declaraciones)
        except Exception as e:
            print(e)
        return obj, created


def crea_secciones(declaracion, extendida):
    """ 
    Función que guarda/crea la sección de la declaración 
    Uso principal: Crea la sección con los campos maximos que deberá tener
    ....
    Parametros
    ----------
       request:
            Pasa el estado a través del sistema
        folio: str
            Folio de la declaración
        estatus: int
            Variable en el modelo de Secciones llamada COMPLETA=2
        aplica: bool
            Valor obtenido si el check mostrado en pantalla de la sección ha sido seleccionado o no
    """
    todas_secciones = Secciones.objects.filter(parent__isnull=True)

    for s in todas_secciones:
        if SeccionDeclaracion.objects.filter(declaraciones=declaracion,seccion=s).first() is None:

            max=CatCamposObligatorios.objects.filter(seccion__parent=s,es_obligatorio=True,esta_pantalla=True).count()
            print('max ->',max)
            observaciones = Observaciones()
            observaciones.save()
            if extendida:
                sd = SeccionDeclaracion(estatus=SeccionDeclaracion.PENDIENTE,declaraciones=declaracion,num=0,max=max,seccion=s,aplica=True,observaciones=observaciones)
            else:
                sd = SeccionDeclaracion(estatus=SeccionDeclaracion.PENDIENTE,declaraciones=declaracion,num=0,max=31,seccion=s,aplica=True,observaciones=observaciones)
            sd.save()



def cuenta_campos(objeto,campos,modelos):
    """ 
    Función para manejo especial de dos secciones de la declaración
    Uso principal: Obtiene de todos los campos obligatorios de la sección cuales faltan

    """
    num = 0
    faltas = []
    for cc in campos:

        try:
            if cc.tipo==0:
                cval = getattr(objeto, cc.nombre_columna)
                if callable(cval):
                    cval = cval()
            else:
                if isinstance(objeto,BienesPersonas) or isinstance(objeto,InfoPersonalVar):
                    if objeto.tipo()==cc.tipo:
                        cval = getattr(objeto, cc.nombre_columna)
                        if callable(cval):
                            cval = cval()
                    else:
                        cval=True
                else:
                    cval=True

        except Exception as e:
            print(e)
            traceback.print_exc()

            cval = None
        if cval is  None or str(cval) == "":
            num=num-1
            faltas.append({
                'objeto':objeto,
                'tipo':cc.tipo,
                'nombre':cc.nombre_columna,
                'seccion':cc.seccion
            })
    return (num,faltas)


def obtiene_avance(declaracion):
    """ 
    Función que calcula los campos obligatorios faltantes y suma el total de todas las secciones para calcular el porcentaje de avance de la declaración
    
    """
    info_personal_fija = InfoPersonalFija.objects.filter(declaraciones=declaracion).first()
    if info_personal_fija.cat_puestos.codigo > settings.LIMIT_DEC_SIMP:
        extendida = 1;
    else:
        extendida = 0;

    if declaracion is None:
        return (1,1)

    crea_secciones(declaracion, extendida)

    if extendida:
        todas_secciones = Secciones.objects.filter(parent__isnull=False)
    else:
        todas_secciones = Secciones.objects.filter(parent__isnull=False, simp=1)


    mapa_objetos = []
    total = 0
    llenados = 0
    SeccionDeclaracion.objects.filter(seccion__parent__isnull=True).update(num=0)
    faltas = {}
    for s in todas_secciones:
        faltas[s.id]=[]
        try:
            campos_compuestos = list(
                CatCamposObligatorios.objects.filter(seccion=s, es_obligatorio=True, es_principal=False))
            campos_principal = list(
                CatCamposObligatorios.objects.filter(seccion=s, es_obligatorio=True, es_principal=True))
            matriz_campos_principales = {}
            models = {}

            matriz_campos_compuestos = {}
            models_s = {}
            aplica = True

            max_num=0
            try:
                seccion_declaracion  = SeccionDeclaracion.objects.filter(seccion=s,declaraciones=declaracion).first()
                aplica=seccion_declaracion.aplica
            except Exception as e:
                seccion_declaracion=None


            for campo_principal in campos_principal:
                if campo_principal.esta_pantalla:
                    max_num=max_num+1
                if not campo_principal.nombre_tabla in matriz_campos_principales:
                    matriz_campos_principales[campo_principal.nombre_tabla] = []
                matriz_campos_principales[campo_principal.nombre_tabla].append(campo_principal)
                if not campo_principal.nombre_tabla in models:
                    model = next((m for m in apps.get_models() if m._meta.db_table == campo_principal.nombre_tabla), None)
                    models[campo_principal.nombre_tabla] = model

            for campo_principal in campos_compuestos:
                if campo_principal.esta_pantalla:
                    max_num=max_num+1
                if not campo_principal.nombre_tabla in matriz_campos_compuestos:
                    matriz_campos_compuestos[campo_principal.nombre_tabla] = []
                matriz_campos_compuestos[campo_principal.nombre_tabla].append(campo_principal)
                if not campo_principal.nombre_tabla in models_s:
                    model = next((m for m in apps.get_models() if m._meta.db_table == campo_principal.nombre_tabla), None)
                    models_s[campo_principal.nombre_tabla] = model

            total += max_num
            num=max_num
            if aplica and max_num > 0:
                if seccion_declaracion is None:
                    num=0
                else:
                    try:
                        for k, v in models.items():
                            if k=="declaracion_observaciones":
                                    try:
                                        obc  = seccion_declaracion.observaciones.observacion
                                        if obc is None or str(obc)=="":
                                            num= num - 1
                                            faltas[s.id].append({
                                                'objeto': seccion_declaracion.observaciones,
                                                'tipo':0,
                                                'nombre': 'observacion',
                                                'seccion':s
                                            })


                                    except Exception as e:
                                        print(e)
                                        num= num - 1
                            else:
                                if s.url =='representacion-activa':
                                    o = v.objects.filter(declaraciones=declaracion,es_representacion_activa=True).first()

                                elif s.url =='datos-pareja':
                                    o = v.objects.filter(declaraciones=declaracion,es_pareja=True).first()

                                elif s.url =='dependientes-economicos':
                                    o = v.objects.filter(declaraciones=declaracion,es_pareja=False).first()

                                elif s.url=='ingresos-varios':
                                    pid = int(s.parametro)+1
                                    o = v.objects.filter(declaraciones=declaracion,
                                                             cat_tipos_ingresos_varios__id=pid ).first()
                                else:
                                    o = v.objects.filter(declaraciones=declaracion).first()


                                for campo_principal in matriz_campos_principales[k]:
                                    try:

                                        if campo_principal.nombre_columna=='apoyos':
                                            if isinstance(o,ConyugeDependientes):

                                                if o.tiene_apoyos:
                                                    lst=o.dependiente()
                                                    for dependiente in lst:
                                                        try:
                                                            apoyo = Apoyos.objects.filter(beneficiario_infopersonalvar=dependiente).first()
                                                            cuenta = cuenta_campos(apoyo,matriz_campos_compuestos['declaracion_apoyos'],models_s)
                                                            num+=cuenta[0]
                                                            faltas[s.id].append(cuenta[1])
                                                        except Exception as e:
                                                            print (e)
                                                            traceback.print_exc()
                                                            apoyo = None
                                                            cuenta = (1,{})
                                                            num = 1
                                                            faltas[s.id].append(cuenta[1])
                                        else:
                                            bval = getattr(o, campo_principal.nombre_columna)

                                            if callable(bval):
                                                _list = bval()
                                                if _list is None or len(_list) == 0:
                                                    num=num-1
                                                else:
                                                    for bval in _list:
                                                        if isinstance(bval, BienesPersonas):
                                                            cuenta = cuenta_campos(bval,
                                                                                 matriz_campos_compuestos['declaracion_bienespersonas'],
                                                                                 models_s)
                                                            num += cuenta[0]
                                                            faltas[s.id].extend(cuenta[1])
                                                            bval=bval.otra_persona

                                                        for l, r in models_s.items():
                                                            if isinstance(bval,InfoPersonalVar) and l=='declaracion_domicilios' and (isinstance(o,BienesMuebles) or isinstance(o,BienesInmuebles)  or isinstance(o,MueblesNoRegistrables) or isinstance(o,Fideicomisos) ):
                                                                for cc in matriz_campos_compuestos[l]:
                                                                    cval = getattr(bval.domicilios, cc.nombre_columna)

                                                                    if cval is  None or str(cval) == "":
                                                                        num = num - 1
                                                                        faltas[s.id].append({
                                                                            'objeto': bval,
                                                                            'tipo': cc.tipo,
                                                                            'nombre': cc.nombre_columna,
                                                                            'seccion': s
                                                                        })

                                                            elif isinstance(bval, r):
                                                                for cc in matriz_campos_compuestos[l]:
                                                                    try:

                                                                        if cc.tipo==0:

                                                                            cval = getattr(bval, cc.nombre_columna)


                                                                            if  cc.nombre_columna=='razon_social' and isinstance(bval,InfoPersonalVar):
                                                                                cval = bval.nombre_completo()
                                                                        elif isinstance(bval,InfoPersonalVar) or isinstance(bval,BienesPersonas):

                                                                            if bval.tipo() == cc.tipo:
                                                                                cval = getattr(bval, cc.nombre_columna)
                                                                                if callable(cval):
                                                                                    cval = cval()
                                                                                else:
                                                                                    cval = True
                                                                            else:
                                                                                cval = True

                                                                    except Exception as e:
                                                                        print (e)
                                                                        traceback.print_exc()
                                                                        cval = None
                                                                    if cval is None or str(cval) == "":
                                                                            num = num - 1
                                                                            faltas[s.id].append({
                                                                                'objeto': bval,
                                                                                'tipo': cc.tipo,
                                                                                'nombre': cc.nombre_columna,
                                                                                'seccion':s
                                                                            })
                                            else:
                                                if bval is None or str(bval) == "":
                                                    num = num - 1
                                                    if campo_principal.esta_pantalla:
                                                        faltas[s.id].append({
                                                            'objeto': o,
                                                            'tipo': campo_principal.tipo,
                                                            'nombre': campo_principal.nombre_columna
                                                        })
                                    except Exception as e:
                                        print(e)
                                        traceback.print_exc()
                                        if campo_principal.esta_pantalla:
                                            faltas[s.id].append({
                                                'objeto': o,
                                                'tipo': campo_principal.tipo,
                                                'nombre': campo_principal.nombre_columna
                                            })
                    except Exception as e:
                        print(e)
                        traceback.print_exc()
                        if campo_principal.esta_pantalla:
                            faltas[s.id].append({
                                'objeto': o,
                                'tipo': campo_principal.tipo,
                                'nombre': campo_principal.nombre_columna,
                                'seccion':s
                            })

            if 0>num:
                num=0
            try:
                pc = int(float(num) / float(max_num) * 100)
            except:
                pc = 0

            if seccion_declaracion is not None:
                seccion_declaracion.num=num
                seccion_declaracion.max=max_num
                seccion_declaracion.save()
                try:
                    padre = SeccionDeclaracion.objects.filter(seccion=seccion_declaracion.seccion.parent,declaraciones=declaracion).first()
                    padre.num=padre.num+num
                    padre.save()
                except Exception as e:
                    print(e)
                    padre = SeccionDeclaracion(seccion=seccion_declaracion.seccion.parent, num=num,
                                                             max=max_num, estatus=SeccionDeclaracion.PENDIENTE,
                                                             declaraciones=declaracion,aplica=True)
                    padre.save()

            mapa_objetos.append({
                'nombre': str(s),
                'llenado': num,
                'total': max_num,
                'porcentaje': pc,
                'seccion':s.id
            })
            llenados += num
        except Exception as e:
            print(e)
            traceback.print_exc()

    try:
        declaracion.avance = int(float(llenados) / float(total) * 100)

        declaracion.save()
    except:
        pass
        print('faltas-------------------------------------------->',faltas[42])
    return (declaracion.avance,faltas)


def actualizar_ingresos(declaracion):
    ingresos_pareja = 0
    ingreso_neto_pareja_dependientes = ConyugeDependientes.objects.filter(declaraciones=declaracion)
    seccion_declaracion_pareja = SeccionDeclaracion.objects.filter(declaraciones=declaracion, seccion=7).first() # 7:pareja
    seccion_declaracion_dependiente = SeccionDeclaracion.objects.filter(declaraciones=declaracion, seccion=8).first() # 8:Dependientes

    aplica_pareja = False
    aplica_dependiente = False

    try:
        if seccion_declaracion_pareja:
            if seccion_declaracion_pareja.aplica:
                aplica_pareja = seccion_declaracion_pareja.aplica

        if seccion_declaracion_dependiente:
            if seccion_declaracion_dependiente.aplica:
                aplica_dependiente = seccion_declaracion_dependiente.aplica

        #Se precargan el salario mensual de todos los dependientes economicos previamente registrados
        if ingreso_neto_pareja_dependientes:
            for ingresos in ingreso_neto_pareja_dependientes:
                if ingresos.actividadLaboralSector:
                    if ingresos.actividadLaboralSector.salarioMensualNeto:
                        if (ingresos.es_pareja and aplica_pareja) or (not ingresos.es_pareja and aplica_dependiente):
                            ingresos_pareja+=int(ingresos.actividadLaboralSector.salarioMensualNeto)

        return (ingresos_pareja)
    except Exception as e:
        raise e
    
def get_declaracion_anterior(declaracion_en_curso):
    declaracion_anterior = None
    try:
        declaraciones_usuario = Declaraciones.objects.filter(info_personal_fija = declaracion_en_curso.info_personal_fija, cat_estatus__pk__in=[3,4])
        if len(declaraciones_usuario) > 2:
            declaracion_anterior = declaraciones_usuario[len(declaraciones_usuario)-2:][0]
        else:
            declaracion_anterior = declaraciones_usuario.first()

        return declaracion_anterior
    except Exception as e:
        raise e

def set_declaracion_extendida_simplificada(info_persona_fija):
    """ 
    Función obtiene el nivel del puesto del usuario para mostrar los datos
    ya sea de una declaración extendida o simplificada
    ...
    Parametros
    ----------
    info_persona_fija = Object InfoPersonalFija del usuario
    
    Validaciones
    ------------
    nivel(codigo en catPuestos) < 15 = Simplificada

    """
    secciones_data = Secciones.objects.filter(parent__isnull=False)
    secciones_por_tipo_declaracion = {}
    puesto_nivel = None
    declaracion_simplificada = False

    try:
        if info_persona_fija.cat_puestos:
            puesto_nivel = info_persona_fija.cat_puestos.codigo
        else:
            puesto_nivel = info_persona_fija.puesto
            puesto_nivel = CatPuestos.objects.filter(puesto__icontains=puesto_nivel).first().codigo
        
        if int(puesto_nivel) <= settings.LIMIT_DEC_SIMP:
            secciones_data = secciones_data.filter(simp=1)
            declaracion_simplificada = True

    except Exception as e:
        secciones_data = secciones_data
    
    for seccion in secciones_data:
        secciones_por_tipo_declaracion.update({seccion.url: True})

    return {
        'secciones_por_tipo_declaracion': secciones_por_tipo_declaracion,
        'declaracion_simplificada': declaracion_simplificada
    }