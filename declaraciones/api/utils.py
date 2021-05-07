from math import ceil
from uuid import UUID
ASC_DESC_ENUM = [
    "asc", "desc"
]


###
# Maps the request sort structure to the
#  django ORM's required argument to apply,
#  a sort (order_by), depending on the specified data.
###
sort_structure = {
    "nombres": "info_personal_fija__nombres",
    "primerApellido": "info_personal_fija__apellido1",
    "segundoApellido": "info_personal_fija__apellido2",
    "escolaridadNivel": "datoscurriculares__cat_grados_academicos__codigo",
    "datosEmpleoCargoComision": {
        "nombreEntePublico": "encargos__nombre_ente_publico",
        "entidadFederativa": "encargos__domicilios__cat_entidades_federativas__codigo",
        "municipioAlcaldia": "encargos__domicilios__municipio__clave",
        "empleoCargoComision": "encargos__cat_puestos__puesto",
        "nivelEmpleoCargoComision": "encargos__nivel_encargo",
        "nivelOrdenGobierno": "encargos__cat_ordenes_gobierno__codigo"
    },
    "totalIngresosNetos": "ingresosdeclaracion__ingreso_mensual_neto",
    "bienesInmuebles": {
        "superficieConstruccion": "bienesinmuebles__superficie_construccion",
        "superficieTerreno": "bienesinmuebles__superficie_terreno",
        "formaAdquisicion": "bienesinmuebles__cat_formas_adquisiciones__codigo",
        "valorAdquisicion": "bienesinmuebles__precio_adquisicion"
    },
}

###
# Maps the request query structure to the
#  django ORM's required argument to apply,
#  a SELECT/WHERE (filter), depending on the specified data.
###
query_structure = {
    "id": "id__icontains",
    "nombres": "info_personal_fija__nombres__icontains",
    "primerApellido": "info_personal_fija__apellido1__icontains",
    "segundoApellido": "info_personal_fija__apellido2__icontains",
    "escolaridadNivel": "datoscurriculares__cat_grados_academicos__codigo__icontains",
    "datosEmpleoCargoComision": {
        "nombreEntePublico": "encargos__nombre_ente_publico__icontains",
        "entidadFederativa": "encargos__domicilios__cat_entidades_federativas__codigo__icontains",
        "municipioAlcaldia": "encargos__domicilios__municipio__clave__icontains",
        "empleoCargoComision": "encargos__cat_puestos__puesto__icontains",
        "nivelOrdenGobierno": "encargos__cat_ordenes_gobierno__codigo__icontains",
        "nivelEmpleoCargoComision": "encargos__nivel_encargo__icontains"
    },
    "bienesInmuebles": {
        "formaAdquisicion": "bienesinmuebles__cat_formas_adquisiciones__codigo__icontains",
        "superficieConstruccion": {
            "min": "bienesinmuebles__superficie_construccion__gte",
            "max": "bienesinmuebles__superficie_construccion__lte"
        },
        "superficieTerreno": {
            "min": "bienesinmuebles__superficie_terreno__gte",
            "max": "bienesinmuebles__superficie_terreno__lte"
        },
        "valorAdquisicion": {
            "min": "bienesinmuebles__precio_adquisicion__gte",
            "max": "bienesinmuebles__precio_adquisicion__lte"
        }
    },
    "totalIngresosNetos": {
        "min": "ingresosdeclaracion__ingreso_mensual_neto__gte",
        "max": "ingresosdeclaracion__ingreso_mensual_neto__lte"
    },
    # "rfcSolicitante": "info_personal_fija__primer_apellido2" # RELATION PENDING
}


def check_valid_value(value, valid_values):
    """ Returns None if the received `value`
    is not contained in the received `valid_values`
    """
    if value in valid_values:
        return value
    return None


def serialize_sort(sort_structure, sort_data):
    """ Given a `sort_structure` dictionary (map from schema),
    and a `sort_data` dictionary (sort payload data received from the user),
    return a list with valid `sort_structure` values in order
    to be used as an argumetn for the query_set `order_by` method.
    """
    # Remove extra keys
    for extra_key in (sort_data.keys() - sort_structure.keys()): del sort_data[extra_key]
    # Iterate items: key, value, apply recursive if both structrues are dicts else 
    #  sanitize by enum asc/desc validation
    for key, value in sort_structure.items():

        if key not in sort_data: continue

        if type(value) == dict and type(sort_data.get(key)) == dict:
            sort_data[key] = serialize_sort(sort_structure.get(key), sort_data.get(key))

        else:
            if check_valid_value(sort_data.get(key), ASC_DESC_ENUM) is None:
                del sort_data[key]
            else:
                sort_data[key] = ("" if sort_data.get(key) == "asc" else "-") + value
                '''if key == "formaAdquisicion":
                    sort_data[key] = ("-" if sort_data.get(key) == "asc" else "") + value
                else:
                    sort_data[key] = ("" if sort_data.get(key) == "asc" else "-") + value'''
                
    return sort_data


def clean_integer_value(
    value,
    exception_type_default=None,
    min_value=None, max_value=None
):
    """ Sanitize the received argument `value`,
    in order for it to comply to the given logic
    contained in the arguments `min_value` and `max_value`
    """
    try:
        if value <= 0:
            value = 10
            
        value = int(value)
        value = min_value if (min_value is not None and value < min_value) else value
        value = max_value if (max_value is not None and value > max_value) else value
    except ValueError as e:
        
        if exception_default is not None:
            return exception_default
        else:
            raise e
    return value

def recursive_dict_to_list(dict_data):
    """ Returns a list containing all values from
    a dictionary and any child contained dictionary.
    """
    list_data = []
    for v in dict_data.values():
        if type(v) == dict:
            for v1 in recursive_dict_to_list(v):
                list_data.append(v1)
        else:
            list_data.append(v)
    return list_data


def sanitize_sort_parameters(sort_structure, sort_data):
    # Return None if it's not a "js object"/ dict or is type None
    if sort_data is None or type(sort_data) != dict:
        return None
    sort_data = serialize_sort(sort_structure, sort_data)
    return recursive_dict_to_list(
        sort_data
    )


def get_page(
    elements,
    page_number,
    page_size,
    min_page_size=1,
    max_page_size=200,
    pagination_data=None
):
    """
    Returns the pagination information
    given the received `elements`
    by calculating the current page (`page_number`),
    `page_size`, `totalRows` (total elements in the \
    given page), and `hasNextPage` (if page number +1)
    will exist given the same arguments.
    """
    elements_length = len(elements)

    if elements_length == 0:
        if pagination_data is not None:
            pagination_data["page"] = 1
            pagination_data["pageSize"] = 1
            pagination_data["totalRows"] = 0
            pagination_data["hasNextPage"] = False
        return []

    # Get page size.    
    page_size = clean_integer_value(
        page_size,
        exception_type_default=min_page_size,
        min_value=min_page_size,
        max_value=max_page_size
    )
    
    # Get max number of pages.
    total_pages = int(ceil(elements_length / page_size))
    total_pages = total_pages if total_pages != 0 else 0
    
    # Clean page number
    '''page_number = clean_integer_value(
        page_number,
        min_value=1,
        max_value=total_pages
    )'''

    #####
    # Slice elements
    #####

    return_elements = elements[
        (page_size*(page_number-1)):(page_size*page_number)
    ]

    # if pagination_data and type(pagination_data) == dict:
    pagination_data["pageSize"] = page_size
    #pagination_data["totalRows"] = len(return_elements)
    pagination_data["totalRows"] = elements_length
    pagination_data["hasNextPage"] = page_number < total_pages
    pagination_data["page"] = page_number
    return return_elements


def api_query_filter(api_query_dict, query_structure):
    if "id" in api_query_dict:
        _key = "folio"
        try:
            _id = api_query_dict.get("id")
            if not _id:
                return{}
            try:
                _id = UUID(_id)
            except ValueError:
                return {_key: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}
                '''_key = "folio"
                _id = ""
                first = int(_id[0])
                if first:
                    _id = first
                else:
                    _id = ""'''
        except:
            _id = 0
        return {_key: _id}

    
    filter_args = {}

    if "nombres" in api_query_dict:
        filter_args[query_structure["nombres"]] = api_query_dict.get("nombres")
    if "primerApellido" in api_query_dict:
        filter_args[query_structure["primerApellido"]] = api_query_dict.get("primerApellido")
    if "segundoApellido" in api_query_dict:
        filter_args[query_structure["segundoApellido"]] = api_query_dict.get("segundoApellido")
    if "escolaridadNivel" in api_query_dict:
        filter_args[query_structure["escolaridadNivel"]] = \
        api_query_dict.get("escolaridadNivel")
        pass
    if "datosEmpleoCargoComision" in api_query_dict:
        if "nombreEntePublico" in api_query_dict["datosEmpleoCargoComision"]:
            filter_args[query_structure["datosEmpleoCargoComision"]["nombreEntePublico"]] = \
            api_query_dict["datosEmpleoCargoComision"]["nombreEntePublico"]
        if "entidadFederativa" in api_query_dict["datosEmpleoCargoComision"]:
            filter_args[query_structure["datosEmpleoCargoComision"]["entidadFederativa"]] = \
            api_query_dict["datosEmpleoCargoComision"]["entidadFederativa"]
        if "municipioAlcaldia" in api_query_dict["datosEmpleoCargoComision"]:
            filter_args[query_structure["datosEmpleoCargoComision"]["municipioAlcaldia"]] = \
            api_query_dict["datosEmpleoCargoComision"]["municipioAlcaldia"]
        if "empleoCargoComision" in api_query_dict["datosEmpleoCargoComision"]:
            filter_args[query_structure["datosEmpleoCargoComision"]["empleoCargoComision"]] = \
            api_query_dict["datosEmpleoCargoComision"]["empleoCargoComision"]
        if "nivelEmpleoCargoComision" in api_query_dict["datosEmpleoCargoComision"]:
            filter_args[query_structure["datosEmpleoCargoComision"]["nivelEmpleoCargoComision"]] = \
            api_query_dict["datosEmpleoCargoComision"]["nivelEmpleoCargoComision"]
        if "nivelOrdenGobierno" in api_query_dict["datosEmpleoCargoComision"]:
            filter_args[query_structure["datosEmpleoCargoComision"]["nivelOrdenGobierno"]] = \
            api_query_dict["datosEmpleoCargoComision"]["nivelOrdenGobierno"]
    if "bienesInmuebles" in api_query_dict:
        if "superficieConstruccion" in api_query_dict["bienesInmuebles"]:
            if "min" in api_query_dict["bienesInmuebles"]["superficieConstruccion"]:
                filter_args[
                    query_structure["bienesInmuebles"]["superficieConstruccion"]["min"]
                ] = \
                api_query_dict["bienesInmuebles"]["superficieConstruccion"]["min"]
            if "max" in api_query_dict["bienesInmuebles"]["superficieConstruccion"]:
                filter_args[
                    query_structure["bienesInmuebles"]["superficieConstruccion"]["max"]
                ] = \
                api_query_dict["bienesInmuebles"]["superficieConstruccion"]["max"]
        if "superficieTerreno" in api_query_dict["bienesInmuebles"]:
            if "min" in api_query_dict["bienesInmuebles"]["superficieTerreno"]:
                filter_args[
                    query_structure["bienesInmuebles"]["superficieTerreno"]["min"]
                ] = \
                api_query_dict["bienesInmuebles"]["superficieTerreno"]["min"]
            if "max" in api_query_dict["bienesInmuebles"]["superficieTerreno"]:
                filter_args[
                    query_structure["bienesInmuebles"]["superficieTerreno"]["max"]
                ] = \
                api_query_dict["bienesInmuebles"]["superficieTerreno"]["max"]
            
        if "formaAdquisicion" in api_query_dict["bienesInmuebles"]:
            filter_args[query_structure["bienesInmuebles"]["formaAdquisicion"]] = \
                api_query_dict["bienesInmuebles"]["formaAdquisicion"]

        if "valorAdquisicion" in api_query_dict["bienesInmuebles"]:
            if "min" in api_query_dict["bienesInmuebles"]["valorAdquisicion"]:
                filter_args[
                    query_structure["bienesInmuebles"]["valorAdquisicion"]["min"]
                ] = \
                api_query_dict["bienesInmuebles"]["valorAdquisicion"]["min"]
            if "max" in api_query_dict["bienesInmuebles"]["valorAdquisicion"]:
                filter_args[
                    query_structure["bienesInmuebles"]["valorAdquisicion"]["max"]
                ] = \
                api_query_dict["bienesInmuebles"]["valorAdquisicion"]["max"]
    
    if "totalIngresosNetos" in api_query_dict:
        filter_args["ingresosdeclaracion__tipo_ingreso"] = True
        if "min" in api_query_dict["totalIngresosNetos"]:
            filter_args[query_structure["totalIngresosNetos"]["min"]]= api_query_dict["totalIngresosNetos"]["min"]
        if "max" in api_query_dict["totalIngresosNetos"]:
            filter_args[query_structure["totalIngresosNetos"]["max"]]= api_query_dict["totalIngresosNetos"]["max"]

    return filter_args


def recursive_serialize_check(objects):
    if type(objects) == list:
        for obj in objects:
            return recursive_serialize_check(obj)
    if type(objects) == tuple:
        for obj in objects:
            return recursive_serialize_check(obj)
    if type(objects) == dict:
        for k, v in objects.items():
            if k == "id":
                continue
            if type(v) == list:
                recursive_serialize_check(v)
            elif type(v) == tuple:
                recursive_serialize_check(v)
            elif type(v) == dict:
                recursive_serialize_check(v)
            elif type(v) != str and type(v) != int and type(v) != float and v is not None and type(v) != bool and type(v) != Decimal:
                print(k, v, type(v))
                import pdb; pdb.set_trace()
        return 
    v = objects
    if type(v) != str and type(v) != int and type(v) != float and v is not None and type(v) != bool and type(v) != Decimal:
        print(v, type(v))
        import pdb; pdb.set_trace()
    pass


def api_query_filter_datosempleocargocomision(declaraciones, api_query_dict={}, sort_data=[]):
    parametros = []
    parametros_sort_e = {}
    parametros_sort_n = {}
    filter_args = {'cat_puestos__isnull':False}
    declaraciones = declaraciones.distinct()

    if "datosEmpleoCargoComision" in api_query_dict:
        if "entidadFederativa" in api_query_dict["datosEmpleoCargoComision"]:
            filter_args["domicilios__cat_entidades_federativas__codigo__icontains"] = \
            api_query_dict["datosEmpleoCargoComision"]["entidadFederativa"]

        if "nombreEntePublico" in api_query_dict["datosEmpleoCargoComision"]:
            filter_args["nombre_ente_publico__icontains"] = \
            api_query_dict["datosEmpleoCargoComision"]["nombreEntePublico"]
            
        if "municipioAlcaldia" in api_query_dict["datosEmpleoCargoComision"]:
            filter_args["domicilios__municipio__clave__icontains"] = \
            api_query_dict["datosEmpleoCargoComision"]["municipioAlcaldia"]
            
        if "empleoCargoComision" in api_query_dict["datosEmpleoCargoComision"]:
            filter_args["cat_puestos__puesto__icontains"] = \
            api_query_dict["datosEmpleoCargoComision"]["empleoCargoComision"]
           
        if "nivelEmpleoCargoComision" in api_query_dict["datosEmpleoCargoComision"]:
            filter_args["nivel_encargo__icontains"] = \
            api_query_dict["datosEmpleoCargoComision"]["nivelEmpleoCargoComision"]

        if "nivelOrdenGobierno" in api_query_dict["datosEmpleoCargoComision"]:
            filter_args["cat_ordenes_gobierno__codigo__icontains"] = \
            api_query_dict["datosEmpleoCargoComision"]["nivelOrdenGobierno"]
    
    for declaracion in declaraciones:
        encargos = declaracion.encargos_set.filter(**filter_args)
        for encargo in encargos:
            #Doble validación para solo obtener el encargo correspondiente al declarante
            if not declaraciones.filter(conyugedependientes__actividadLaboralSector=encargo.id):
                parametros.append(encargo.id)
                parametros_sort_e.update({encargo.pk: encargo.cat_puestos.puesto})
                parametros_sort_n.update({encargo.pk: encargo.nivel_encargo})
    
    parametros = list(dict.fromkeys(parametros))
    
    declaraciones = declaraciones.filter(encargos__cat_puestos__isnull=False,encargos__in=parametros)
    
    return declaraciones

def api_query_filter_ingresos(declaraciones):
    return declaraciones.filter(**{"ingresosdeclaracion__tipo_ingreso": True})

def api_estadisticas_query(api_query_dict):
    filter_args = {}
    structure = {
        "declaracion":{
            "tipo": "cat_tipos_declaracion__codigo__icontains",
            "estatus":"cat_estatus__codigo__icontains",
            "fechaDeclaracion":"fecha_declaracion",
            "fechaRecepcion":"fecha_recepcion__startswith",
            "datosPublicos": "datos_publicos"
        },
        "usuario":{
            "fechaIngreso":"fecha_inicio",
            "puesto":"puesto__icontains"
        },
        "entePublico": "nombre_ente_publico__icontains"
    }

    if "declaracion" in api_query_dict:
        filter_args["declaracion"] = {}
        if "tipo" in api_query_dict["declaracion"]:
            filter_args["declaracion"][structure["declaracion"]["tipo"]] = api_query_dict["declaracion"].get("tipo")
        if "estatus" in api_query_dict["declaracion"]:
            filter_args["declaracion"][structure["declaracion"]["estatus"]] = api_query_dict["declaracion"].get("estatus")
        if "fechaDeclaracion" in api_query_dict["declaracion"]:
            filter_args["declaracion"][structure["declaracion"]["fechaDeclaracion"]] = api_query_dict["declaracion"].get("fechaDeclaracion")
        if "datosPublicos" in api_query_dict["declaracion"]:
            filter_args["declaracion"][structure["declaracion"]["datosPublicos"]] = api_query_dict["declaracion"].get("datosPublicos")
        if "fechaRecepcion" in api_query_dict["declaracion"]:
            fecha = api_query_dict["declaracion"].get("fechaRecepcion").split("-")
            fecha = list(map(int,fecha))
            filter_args["declaracion"][structure["declaracion"]["fechaRecepcion"]] = datetime.date(fecha[0],fecha[1],fecha[2])

    if "usuario" in api_query_dict:
        filter_args["usuario"] = {}
        if "fechaIngreso" in api_query_dict["usuario"]:
            filter_args["usuario"][structure["usuario"]["fechaIngreso"]] = api_query_dict["usuario"].get("fechaIngreso")
        if "puesto" in api_query_dict["usuario"]:
            filter_args["usuario"][structure["usuario"]["puesto"]] = api_query_dict["usuario"].get("puesto")

    if "entePublico" in api_query_dict:
        filter_args[structure["entePublico"]] = api_query_dict.get("entePublico")
    
    return filter_args