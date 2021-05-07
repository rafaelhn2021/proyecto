$(document).ready(function(){
    //Si una declaración es nueva se mostrara un mensaje al usuario
    if("{{nueva_declaracion}}" == "True")
    {
      $('#mensaje_bienvenida').modal('show');
    }
 });

/*** Declaración fisal */
//Se encarga de procesar el archivo que sea cargado en el input type
function readURL(input)
{
   var tipo = input.getAttribute('tipo');
   if(input.files && input.files[0])
   {
     var reader = new FileReader();
     reader.onload = function(e) {
       $('#image-upload-wrap-'+tipo).hide();
       $('#file-upload-content-'+tipo).show();
       $('#image-title-'+tipo).html(input.files[0].name);
     };
     reader.readAsDataURL(input.files[0]);
   }
   else 
   {
      removeUpload(tipo);
   }
}

//Elimina el archivo cargado en la zona 
function removeUpload(tipo)
{
  $('declaracion_fiscal-archivo_'+tipo).replaceWith($('declaracion_fiscal-archivo_').clone());
  $('#file-upload-content-'+tipo).hide();
  $('#image-upload-wrap-'+tipo).show();
}

$('.image-upload-wrap').bind('dragover', function () {
  $('.image-upload-wrap').addClass('image-dropping');
});

$('.image-upload-wrap').bind('dragleave', function () {
  $('.image-upload-wrap').removeClass('image-dropping');
});
// función para borrar usuarios
function borraUsuario(url,form,reload){
  var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
  function csrfSafeMethod(method) {
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });
  console.log("AQUI--"+url.replace('0',$("#id-usuario").val()));
      $.ajax({
          url : url.replace('0',$("#id-usuario").val()),
          type : "POST",
          data:$("#"+form).serialize(),
          success : function(json) {
              if(reload===true) {
                  $("#id-usuario-" + $("#id-usuario").val()).remove();
                  $("#id-usuario").val("")
                  $("#nombre-usuario").html("")
                  $("#modal").modal('hide');
              } else{
                  window.location.href =reload;
              }
          },
          error : function(xhr,errmsg,err) {

          }
      });

};

// functión para borrar registros
function borrarRegistro(url, redirect, id) {
  var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
  function csrfSafeMethod(method) {
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });

  if (confirm('¿Está seguro de eliminar el registro?aefd') == true) {
      $.ajax({
          url : url,
          type : "POST",
          success : function(json) {
            $("#borrar-registro-" + id).hide()
          },
          error : function(xhr,errmsg,err) {
              console.log(xhr.status + ": " + xhr.responseText);
          }
      });
  } else {
      return false;
  }
};
// funcion para tipo de persona
function radioTPersona(v,id){

  if(v=='true'){
      $("#id_"+id+"_container_fisica").show()
      $("#id_"+id+"_container_moral").hide()

  } else{
      $("#id_"+id+"_container_fisica").hide()
      $("#id_"+id+"_container_moral").show()
  }
};
// checkbox para "otros" en los formularios de declaraciones
function checkBoxText(name,other,active){
  if(active){
      $("#"+other).prop("readonly",false);
      $("#"+other).prop("required",true);
      $("#"+other).focus();
  }else{
      $("#"+other).prop("readonly",true);
      $("#"+other).prop("required",false);
      $("#"+other).val("");
  }
};
function checkBoxText2(name,other,active,other2){
  if(active){
      $("#"+other).prop("readonly",false);
      $("#"+other).prop("required",true);
      $("#"+other).focus();
  }else{
      $("#"+other).prop("readonly",true);
      $("#"+other).prop("required",false);
      $("#"+other).val("");
  }
  $("#"+other2).val("")
  $("#"+other2).prop("readonly",true);
};
// función para ocultar select  de paises cuando no es extranjero en apartado de nacionalidad
function radioMx(v,id){
  /*if(op==0){
    $("#id_domicilio-cat_pais").hide();
    $("#id_datos_curriculares-cat_pais").hide();
    $("#id_inmueble_domicilio-cat_pais").hide();
  }else{
    $("#id_domicilio-cat_pais").show();
    $("#id_datos_curriculares-cat_pais").show();
    $("#id_inmueble_domicilio-cat_pais").show();
  }*/
  if(v==='mx'){
    $("#"+id).val(141)
    $("#"+id+"_container").hide()
  } else{
      $("#"+id+"_container").show()
  }
}

// función para el no_aplica de las declaraciones
function no_aplica_fun(check){
  if(check.checked){
    $(".row-form").hide();
  }else {
    $(".row-form").show();
  }
  alert("si");
}

$(document).ready(function() {
 
  if($("#hide_nueva_declaracion").val() == "True")
  {
    $('#mensaje_bienvenida').modal('show');
  }
  //Muestra ventana emergente para seleccionar el tipo de reporte a generar
  //Modulo Admin/busqueda-declaraciones
  $("#ventana-modal").on('show.bs.modal', function(){
    var inputs = $('#form_declaraciones :input');
    var values = {};

    inputs.each(function(){
      var name_imput = $(this).attr('name');
      if(name_imput != "estatus" && name_imput != "tipo"){
        values[name_imput] = $(this).val();
      }
      else{
        values[name_imput] = $(this).children("option:selected").val();
      }
    });

    var form_reporte = $('#form_declaraciones_reporte :input');
    form_reporte.each(function(i, input){
      $(input).val(values[$(input).attr('name')])
    });
  });
  /*******************************VALIDACIONES DE INICIALIZACIÓN**************************************************/
  var estado_civil = parseInt($("#id_var-cat_estados_civiles").val());
  if(!$('#id_var-cat_regimenes_matrimoniales').val()){
    $('#id_var-cat_regimenes_matrimoniales').attr("disabled", true);
  }
  else
  {
    if( estado_civil == 2 || estado_civil == 3){
      $('#id_var-cat_regimenes_matrimoniales').attr("disabled", true);
      $('#id_var-cat_regimenes_matrimoniales').val("");
    }
  }

  var date = new Date();
  var year = date.getFullYear();

  muebles_forma_pago_inicial('id_bienes_inmuebles');
  muebles_forma_pago_inicial('id_muebles_no_registrables');
  muebles_forma_pago_inicial('id_bienes_muebles'); 
  graficas_ajax_api({"anio":year});
  
  /*****************************************FUNCIONES CHANGE**************************************************/
  //Se encarga de habilitar o no el campo de regimenes matrimoniales de acuerdo al estado civil
  $("#id_var-cat_estados_civiles").change(function(){
    estado_civil = parseInt($(this).children("option:selected").val());
    if(estado_civil == 2 || estado_civil == 3){
      $('#id_var-cat_regimenes_matrimoniales').attr("disabled", true);
      $('#id_var-cat_regimenes_matrimoniales').val("");
    }
    else{
      $('#id_var-cat_regimenes_matrimoniales').attr("disabled", false);
    }
  });

  //Habilita o deshabilita campos monto y moneda en bienes muebles y no registrables
  $("#id_bienes_inmuebles-forma_pago").change(function(){
    muebles_forma_pago($(this),'id_bienes_inmuebles');
  });
  $("#id_muebles_no_registrables-forma_pago").change(function(){
    muebles_forma_pago($(this),'id_muebles_no_registrables');
  });
  $("#id_bienes_muebles-forma_pago").change(function(){
    muebles_forma_pago($(this),'id_bienes_muebles');
  });

  //Para la sección de conyugue-dependieentes
  $("#id_datos_pareja-actividadLaboral").change(function(){
    change_conyugue($(this),'datos-pareja');
  });
  $("#id_conyuge_dependiente-actividadLaboral").change(function(){
    change_conyugue($(this),'datos-dependiente');
  });

  //Para sección de INGRESOS
  $("#id_ingresos_declaracion-ingreso_mensual_cargo").change(function(){
    change_ingresos_suma($(this));
  });

  $("#id_ingresos_declaracion-ingreso_mensual_actividad").change(function(){
    change_ingresos_suma($(this));
  });

  $("#id_ingresos_declaracion-ingreso_mensual_financiera").change(function(){
    change_ingresos_suma($(this));
  });

  $("#id_ingresos_declaracion-ingreso_mensual_servicios").change(function(){
    change_ingresos_suma($(this));
  });

  $("#id_ingresos_declaracion-ingreso_otros_ingresos").change(function(){
    change_ingresos_suma($(this));
  });

  $("#id_ingresos_declaracion-ingreso_enajenacion_bienes").change(function(){
    change_ingresos_suma($(this));
  });

  $('#id_anio_filtro_year').change(function(){
    graficas_ajax_api({"anio":$(this).val()});
  });

  $('input[type=radio][name="experiencia_laboral-cat_ambitos_laborales"]').change(function() {
    if($(this).val() == 1){
      $(".ambito_publico").show();
    }else{
      $(".ambito_publico").hide();
    }
  });
  
  //Valida si el dato de remuneración ya esta guardado
  $('#id_socios_comerciales-montoMensual').attr("disabled", true);
  $('#id_socios_comerciales-moneda').attr("disabled", true);
  $("#id_domicilio-cat_entidades_federativas").on("change", getMunicipios);           
 
});

//Carga información de gráficas cuando el usuario es staff en declaraciones
function graficas_ajax_api(data){
var canvas1 = document.getElementById("chart_grafica_usuarios_declaraciones_general");
var canvas2 = document.getElementById("chart_grafica_usuario_declaraciones_fechas");

if(canvas1 || canvas2){
  document.getElementById("grafica_usuarios_declaraciones_general").innerHTML = '&nbsp;';
  document.getElementById("grafica_usuarios_declaraciones_general").innerHTML = '<canvas id="chart_grafica_usuarios_declaraciones_general"></canvas>';
  
  document.getElementById("grafica_usuario_declaraciones_fechas").innerHTML = '&nbsp;';
  document.getElementById("grafica_usuario_declaraciones_fechas").innerHTML = '<canvas id="chart_grafica_usuario_declaraciones_fechas"></canvas>';
}

$.ajax({ 
  method: "GET",
  data: data,
  url: "{% url 'declaracion:api-graficas-data' %}",
  success: function(data) {
    $("#filtro_anio_graficas div.row.bootstrap4-multi-input").children().each(function(){
      var name_input=$(this).children()[0].name;
      if(name_input != "anio_filtro_year"){
        $(this).css("display","none");
      }
    });
    drawBarGraph(data, 'chart_grafica_usuarios_declaraciones_general');
    drawLineGraph(data, 'chart_grafica_usuario_declaraciones_fechas');
  }, 
  error: function(error_data) {
    console.log(error_data); 
  } 
});
}

function getMunicipios() {
  var entidad_federativa = $("#id_domicilio-cat_entidades_federativas").val();
  var url = $("#formInfoPersonal").attr("data-municipios-url");

  if (entidad_federativa) {
      //Eliminamos las opciones anteriores del select
      $("#id_domicilio-municipio").html("");
      $.ajax({
          url: "{% url 'declaracion:lista_municipios' %}",
          type: "GET",
          data: {
              "entidad_federativa": entidad_federativa,
          },
          success: function(response){
            $("#id_domicilio-municipio").html(response.municipios);
            $("#id_domicilio-municipio").trigger("change");
          }
      });
  } else {
      $("#id_domicilio-municipio").html("<option value='' selected='selected'>---------</option>");
      $("#id_domicilio-municipio").trigger("change");
  }
}    

function accion_hide_disabled_show(_this)
{
//console.log('ESTE ES UN ID',_this.id);
switch(_this.id){
  case 'ingreso_anio_anterior-no':
    $('#div_sueldo_publico_actual').show();
    $('#div_sueldo_publico_anterior').hide();
    $('#div_sueldo_publico_anterior_fi').hide();
    $('#div_sueldo_publico_anterior_fc').hide();

    $('.fechas_anio_anterior').hide();
    $('.fechas_anio_anterior').hide();
  break;

  case 'ingreso_anio_anterior-si':
    $('#div_sueldo_publico_actual').hide();
    $('#div_sueldo_publico_anterior').show();
    $('#div_fue_servidor_publico').show();
    $('#div_sueldo_publico_anterior_fi').show();
    $('#div_sueldo_publico_anterior_fc').show();

    $('.fechas_anio_anterior').show();
    $('.fechas_anio_anterior').show();
  break;

  case 'id-domicilio-cat_pais-ex':
    $('#id_domicilio-colonia').attr("disabled", true);
    $('#id_domicilio-cat_entidades_federativas').attr("disabled", true);
    $('#id_domicilio-municipio').attr("disabled", true);
    $('#id_domicilio-colonia').val("");
    $('#id_domicilio-cat_entidades_federativas').val("");
    $('#id_domicilio-municipio').val("");
  break;

  case 'id-domicilio-cat_pais-mx':
    $('#id_domicilio-colonia').attr("disabled", false);
    $('#id_domicilio-cat_entidades_federativas').attr("disabled", false);
    $('#id_domicilio-municipio').attr("disabled", false);
    $('#id_domicilio-cat_entidades_federativas').val(14);
  break;

  case 'ingresos-no':
    $('#id_socios_comerciales-montoMensual').attr("disabled", true);
    $('#id_socios_comerciales-moneda').attr("disabled", true);
  break;

  case 'ingresos-si':
    $('#id_socios_comerciales-montoMensual').attr("disabled", false);
    $('#id_socios_comerciales-moneda').attr("disabled", false);
  break;

  case 'no-pagado':
    $('#id_membresia-monto').attr("disabled", true);
    $('#id_membresia-moneda').attr("disabled", true);
  break;

  case 'Pagado':
    $('#id_membresia-monto').attr("disabled", false);
    $('#id_membresia-moneda').attr("disabled", false);
  break;

  case 'no-pagado-act':
    $('#id_representaciones_activas-monto').attr("disabled", true);
    $('#id_representaciones_activas-cat_moneda').attr("disabled", true);
  break;

  case 'Pagado-act':
    $('#id_representaciones_activas-monto').attr("disabled", false);
    $('#id_representaciones_activas-cat_moneda').attr("disabled", false);
  break;
}
}

/*** Declaración fiscal */
//Se encarga de procesar el archivo que sea cargado en el input type
function readURL(input)
{
var tipo = input.getAttribute('tipo');
if(input.files && input.files[0])
{
  var reader = new FileReader();
  reader.onload = function(e) {
    $('#image-upload-wrap-'+tipo).hide();
    $('#file-upload-content-'+tipo).show();
    $('#image-title-'+tipo).html(input.files[0].name);
  };
  reader.readAsDataURL(input.files[0]);
}
else 
{
  removeUpload(tipo);
}
}

//Elimina el archivo cargado en la zona de declaración fiscal
function removeUpload(tipo)
{
$('declaracion_fiscal-archivo_'+tipo).replaceWith($('declaracion_fiscal-archivo_').clone());
$('#file-upload-content-'+tipo).hide();
$('#image-upload-wrap-'+tipo).show();
}

$('.image-upload-wrap').bind('dragover',function(){
$('.image-upload-wrap').addClass('image-dropping');
});

$('.image-upload-wrap').bind('dragleave',function(){
$('.image-upload-wrap').removeClass('image-dropping');
});

function change_conyugue(_this, id_div){
var actividad_laboral = parseInt(_this.children("option:selected").val());

  switch(actividad_laboral){
    case 1://PUBLICO
      $('#'+id_div+'-sector-publico').show();
      $('#'+id_div+'-sector-privado').hide();
    break;

    case 2://PRIVADO
      $('#'+id_div+'-sector-publico').hide();
      $('#'+id_div+'-sector-privado').show();
    break;

    default:
      $('#'+id_div+'-sector-publico').hide();
      $('#'+id_div+'-sector-privado').hide();
  }
}

function change_ingresos_suma(_this){
var monto_pareja = $('#id_ingresos_declaracion-ingreso_mensual_pareja_dependientes').val();
var monto_declarante = 0, monto_total = 0, monto_otros = 0;
var id_input_montos = 
[
  'ingreso_mensual_cargo',
  'ingreso_mensual_actividad',
  'ingreso_mensual_financiera',
  'ingreso_mensual_servicios',
  'ingreso_enajenacion_bienes',
  'ingreso_otros_ingresos'
]

for(var i=0;i<id_input_montos.length; i++){
  if($('#id_ingresos_declaracion-'+id_input_montos[i]).val()){
    monto_declarante+=parseInt($('#id_ingresos_declaracion-'+id_input_montos[i]).val())

    if(id_input_montos[i] != 'ingreso_mensual_cargo'){
      monto_otros+=parseInt($('#id_ingresos_declaracion-'+id_input_montos[i]).val())
    }
  }
}

monto_total=monto_total+monto_declarante+parseInt(monto_pareja);

$('#id_ingresos_declaracion-ingreso_mensual_otros_ingresos').val(monto_otros);
$('#id_ingresos_declaracion-ingreso_mensual_neto').val(monto_declarante);
$('#id_ingresos_declaracion-ingreso_mensual_total').val(monto_total);

if((monto_declarante == 0 || monto_declarante==null) && parseInt(monto_pareja)){
  monto_declarante = parseInt(monto_pareja);
}
}

function muebles_forma_pago(_this,_id)
{
var fp = _this.children("option:selected").val();
if(fp == 'CREDITO' || fp == 'CONTADO'){
  $('#'+_id+'-precio_adquisicion').attr("disabled", false);
  $('#'+_id+'-cat_monedas').attr("disabled", false);
}
else{
  $('#'+_id+'-precio_adquisicion').attr("disabled", true);
 $('#'+_id+'-cat_monedas').attr("disabled", true);
}
}

function muebles_forma_pago_inicial(_id)
{
var forma_pago = $('#'+_id+'-forma_pago').val();
if(!forma_pago){
   $('#'+_id+'-precio_adquisicion').attr("disabled", true);
   $('#'+_id+'-cat_monedas').attr("disabled", true);
}
else{
  if(forma_pago == 'CREDITO' || forma_pago == 'CONTADO'){
    $('#'+_id+'-precio_adquisicion').attr("disabled", false);
    $('#'+_id+'-cat_monedas').attr("disabled", false);
  }
  else{
    $('#'+_id+'-precio_adquisicion').attr("disabled", true);
    $('#'+_id+'-cat_monedas').attr("disabled", true);
  }
}
}

