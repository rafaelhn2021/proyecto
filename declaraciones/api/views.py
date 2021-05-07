import json, subprocess, re

from django.http import HttpResponse
from django.core import serializers as serializers_django
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from django.views.decorators.csrf import csrf_exempt

from declaracion.models import Declaraciones,CatTiposDeclaracion,InfoPersonalFija
from django.contrib.auth.models import User

from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from .utils import *
from .serialize_functions import serialize_declaracion, serialize_response_entry
from .validator import get_token_from_request, token_not_expired

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import status, permissions, serializers, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import RetrieveAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from oauth2_provider.views.generic import ProtectedResourceView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope

from declaraciones.settings import EXPIRES_IN_N_MINUTES
from datetime import timedelta


from decimal import Decimal
from datetime import datetime, date
from sitio.models import sitio_personalizacion

default_page = 1
default_size = 10
max_page_size = 200
empty_json_error_auth = '{ "detail": "Credenciales no autorizadas." }'
empty_json_error_auth = json.loads(empty_json_error_auth)


class OauthDeclaraciones(ProtectedResourceView):

    def dispatch(self, request, *args, **kwargs):
        # let preflight OPTIONS requests pass
        if request.method.upper() == "OPTIONS":
            return super().dispatch(request, *args, **kwargs)

        # check if the request is valid and the protected resource may be accessed
        valid, r = self.verify_request(request)
        if valid:
            request.resource_owner = r.user
            return super().dispatch(request, *args, **kwargs)
        else:
            return JsonResponse({"codigo": "700", "descripcion":"token expirado"})

    def post(self, request, *args, **kwargs):

        declaraciones = Declaraciones.objects.filter(cat_estatus=4)

        try:
            json_data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(res_400_error())

        #t_expired= False
        #if t_expired :
        #   response=json.loads('{"code":"700", "description":"Token expirado"}')
        #   return JsonResponse(response)


        page_number = int(json_data.get('page', default_page))

        page_size = clean_integer_value(
            json_data.get('pageSize', default_size),
            exception_type_default=default_size,
            min_value=1, max_value=max_page_size
        )

        query_filter = api_query_filter(
            json_data.get("query", {}), query_structure
        )
        
        if query_filter:
            declaraciones = declaraciones.filter(**query_filter)
            
            if "datosEmpleoCargoComision" in json_data.get("query", {}):
                declaraciones = api_query_filter_datosempleocargocomision(declaraciones,json_data.get("query", {}))

        sort_by = sanitize_sort_parameters(
            sort_structure, json_data.get("sort", {})
        )

        if sort_by:
            if "datosEmpleoCargoComision" in json_data.get("sort", {}):
                declaraciones = api_query_filter_datosempleocargocomision(declaraciones,json_data.get("query", {}))
            if "totalIngresosNetos" in json_data.get("sort", {}):
                declaraciones = api_query_filter_ingresos(declaraciones)

            declaraciones = declaraciones.order_by(*sort_by)

        pagination_data = {}
        declaraciones = get_page(
            declaraciones.all(),
            page_number=page_number,
            page_size=page_size,
            pagination_data=pagination_data
        )
        response = {
            "pagination": {
                "pageSize": pagination_data["pageSize"],
                "totalRows": pagination_data["totalRows"],
                "hasNextPage": pagination_data["hasNextPage"],
                "page": pagination_data["page"]
            },
            "results": [ serialize_response_entry(declaracion) for declaracion in declaraciones ]
        }
        return JsonResponse(response)


class LoginView(jwt_views.TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        try:
            json_data = json.loads(request.body)
            _username = json_data.get('username')
            user = User.objects.get(username=_username)
            if not user.groups.filter(name='api').exists():
                return Response(empty_json_error_auth)
        except Exception :
            return Response(empty_json_error_auth)
        data = super().post(request, *args, **kwargs)
        data.data["token_type"] =  "Bearer"
        data.data["expires_in"] = EXPIRES_IN_N_MINUTES * 60
        return data


class estadisticasView(ProtectedResourceView):
    def dispatch(self, request, *args, **kwargs):
        # let preflight OPTIONS requests pass
        if request.method.upper() == "OPTIONS":
            return super().dispatch(request, *args, **kwargs)

        # check if the request is valid and the protected resource may be accessed
        valid, r = self.verify_request(request)
        if valid:
            request.resource_owner = r.user
            return super().dispatch(request, *args, **kwargs)
        else:
            return JsonResponse({"codigo": "700", "descripcion":"token expirado"})#str(r)})

    def post(self, request, *args, **kwargs):
        try:
            json_data = json.loads(request.body)
        except Exception as e:
            return Response(res_400_error(), status=status.HTTP_400_BAD_REQUEST)
            json_data = {}
        
        response = {
            "declaraciones":
            {
                "resumen":{
                    "iniciales":{},
                    "modificación":{},
                    "conclusión":{}
                },
                "data":[]
            },
            "usuarios":
            {
                "resumen":
                {
                    "activos":0,
                    "baja":0
                },
                "data":[]
            }
        }
        
        try:
            usuarios = User.objects.filter(is_superuser=0)
            declaraciones = Declaraciones.objects.all()

            query_filter = api_estadisticas_query(
                json_data.get("query", {})
            )

            if query_filter:
                if "declaracion" in query_filter:
                    declaraciones = declaraciones.filter(**query_filter["declaracion"])
                if "usuario" in query_filter:
                    infoPersonalF = InfoPersonalFija.objects.filter(**query_filter["usuario"])
                    usuariosF = []
                    for usuario in infoPersonalF:
                        usuariosF.append(usuario.usuario.pk)
                    usuarios = usuarios.filter(pk__in=usuariosF)

            for usuario in usuarios:
                try:
                    usuario_infofija = InfoPersonalFija.objects.get(usuario=usuario.pk)
                    if usuario_infofija:
                        if usuario.is_active:                
                            response["usuarios"]["resumen"]["activos"]=response["usuarios"]["resumen"]["activos"]+1
                        else:
                            response["usuarios"]["resumen"]["baja"]=response["usuarios"]["resumen"]["baja"]+1

                        data_fija = {
                            "id": usuario_infofija.pk,
                            "fecha_ingreso": usuario_infofija.fecha_inicio,
                            "puesto": usuario_infofija.puesto,
                            "declaraciones":[]
                        }

                        declaraciones_fija = declaraciones.filter(info_personal_fija=usuario_infofija.pk)
                        
                        if declaraciones_fija:
                            for dec_fija in declaraciones_fija:
                                data_fija["declaraciones"].append(dec_fija.pk)

                                info_declaracion = {
                                    "id": dec_fija.pk,
                                    "folio": dec_fija.folio,
                                    "tipo": dec_fija.cat_tipos_declaracion.codigo,
                                    "estatus": dec_fija.cat_estatus.estatus_declaracion,
                                    "fecha_declaracion": dec_fija.fecha_declaracion,
                                    "fecha_recepcion": dec_fija.fecha_recepcion if dec_fija.fecha_recepcion else "",
                                    "datos_publicos":dec_fija.datos_publicos
                                }

                                info_declaracion["usuario"] = usuario_infofija.pk
                                response["declaraciones"]["data"].append(info_declaracion)

                        response["usuarios"]["data"].append(data_fija)
                except Exception as e:
                    pass
            
            if declaraciones:
                response["declaraciones"]["resumen"]["iniciales"]["terminadas"] = len(declaraciones.filter(cat_estatus__id=4, cat_tipos_declaracion__codigo='INICIAL'))
                response["declaraciones"]["resumen"]["iniciales"]["por_terminar"] = len(declaraciones.filter(cat_estatus__id=1, cat_tipos_declaracion__codigo='INICIAL'))
                response["declaraciones"]["resumen"]["modificación"]["terminadas"] = len(declaraciones.filter(cat_estatus__id=4, cat_tipos_declaracion__codigo='MODIFICACIÓN'))
                response["declaraciones"]["resumen"]["modificación"]["por_terminar"] = len(declaraciones.filter(cat_estatus__id=1, cat_tipos_declaracion__codigo='MODIFICACIÓN'))
                response["declaraciones"]["resumen"]["conclusión"]["terminadas"] = len(declaraciones.filter(cat_estatus__id=4, cat_tipos_declaracion__codigo='CONCLUSIÓN'))
                response["declaraciones"]["resumen"]["conclusión"]["por_terminar"] = len(declaraciones.filter(cat_estatus__id=1, cat_tipos_declaracion__codigo='CONCLUSIÓN'))
        except Exception as e:
            return JsonResponse(response)

        return JsonResponse(response)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def estadisticasGraficasView(request):
    data = {}

    if request.method == 'GET': 
        try:
            dumps = json.dumps(request.data)
            json_data = json.loads(dumps)
        except Exception as e:
            return Response(res_400_error(), status=status.HTTP_400_BAD_REQUEST)
    
        fecha_inicio = date(date.today().year,1,1)
        fecha_fin = date(date.today().year,12,31)
        declaraciones_por_usuario = {'sin_declaracion':0}
        tipos_declaracion = ['Sin declaración']
        usuarios_activos = 0
        usuarios_baja = 0
        
        var_filter = {"year":date.today().year}
        if json_data:
            if json_data.get('filter') is not None:
                var_filter = json_data.get('filter')
                fecha_inicio = date(int(var_filter["year"]),1,1)
                fecha_fin = date(int(var_filter["year"]),12,31)
    
        #Información que mostrará el promedio de las declaraciones creadas por la cantidad de usuario existentes
        for tipo in CatTiposDeclaracion.objects.all():
            tipos_declaracion.append(tipo.codigo)
            declaraciones_por_usuario.update({tipo.codigo: 0})
        
        usuarios = User.objects.filter(is_superuser=0)
        usuario_infofija = []
        for usuario in usuarios:
            try:
                exists = InfoPersonalFija.objects.get(usuario=usuario.pk,fecha_inicio__range=[fecha_inicio,fecha_fin])
                usuario_infofija.append(exists.pk)
            except Exception as e:
                pass
        
        usuarios_activos = InfoPersonalFija.objects.filter(pk__in=usuario_infofija, usuario__is_active=1)
        usuarios_baja = InfoPersonalFija.objects.filter(pk__in=usuario_infofija, usuario__is_active=0)
    
        declaraciones = Declaraciones.objects.all()
        declaraciones_por_anio = declaraciones.filter(fecha_declaracion__range=[fecha_inicio,fecha_fin])
        for usuario in usuarios_activos:
            usuario_declaraciones = declaraciones_por_anio.filter(info_personal_fija=usuario)
            if usuario_declaraciones.exists():
                for usu_dec in usuario_declaraciones:
                    declaraciones_por_usuario[usu_dec.cat_tipos_declaracion.codigo]+=1;
                else:
                    declaraciones_por_usuario['sin_declaracion']+=1;
    
        chartdata = declaraciones_por_usuario.values()
        #Información que mostrara la cantidad de usuarios y declaraciónes creados por año
        meses = ['Enero', 'Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        if len(usuarios_activos) > len(declaraciones):
            total_usuarios_declaraciones = len(usuarios_activos)
        else:
            total_usuarios_declaraciones = len(declaraciones)
    
        usuarios_por_anio = usuarios.filter(date_joined__range=[fecha_inicio,fecha_fin])
        declaraciones_por_mes={}
        usuarios_por_mes={}
    
        for mes in meses:
            mes_index = meses.index(mes)+1
            declaraciones_mes = declaraciones_por_anio.filter(fecha_declaracion__month=mes_index)
            if declaraciones_mes:
                declaraciones_por_mes.update({mes: len(declaraciones_mes)})
            else:
                declaraciones_por_mes.update({mes:0})
    
            usuarios_mes = usuarios_por_anio.filter(date_joined__month=mes_index)
            if usuarios_mes:
               usuarios_por_mes.update({mes:len(usuarios_mes)})
            else:
               usuarios_por_mes.update({mes:0})
    
        data = {
                "labels":tipos_declaracion,
                "lables_meses": meses,
                "chartLabel":"Declaraciones",
                "chartLabel_usuario":"Usuarios",
                "chartdata":chartdata,
                "total_usuario_activos": len(usuarios_activos),
                "total_usuario_baja": len(usuarios_baja),
                "total_usuarios_declaraciones": total_usuarios_declaraciones,
                "chartdata_datos_anuales_declaraciones": [ mes \
                        for mes in  declaraciones_por_mes.values()],
                "chartdata_datos_anuales_usuarios": [ usuario_mes \
                        for usuario_mes in  usuarios_por_mes.values()],
                "extra_params": [var_filter["year"]]
            }

    return Response(data)


def res_error(code, message):
    """ Unexpected Error response
    """
    return {
        "code": code,
        "message": message
    }


def res_default_error(code=500, message="Unexpected Error response"):
    """ Unexpected Error response
    """
    # code: TBD
    return res_error(code, message)


def res_400_error(code=400, message="Página inválida (bad request)"):
    """ Bad request custom response
    """
    return res_error(code, message)


def res_401_error(code=401, message="acceso no autorizado"):
    """ Auth error response
    """
    return res_error(code, message)
