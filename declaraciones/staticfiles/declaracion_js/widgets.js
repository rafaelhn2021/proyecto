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

function radioMx(v,id){

  if(v==='mx'){
      $("#"+id).val(141);
      $("#"+id+"_container").hide()
  } else{
      $("#"+id+"_container").show()
  }
};

function radioUnica(id){
  if(id=='id-frecuencia-container'){
      $("#id-frecuencia-container").show()
      $("#id-unica-container").hide()
  } else{
      $("#id-frecuencia-container").hide()
      $("#id-unica-container").show()
  }
};

function radioTPersona(v,id){

  if(v=='true'){
      $("#id_"+id+"_container_fisica").show()
      $("#id_"+id+"_container_moral").hide()

  } else{
      $("#id_"+id+"_container_fisica").hide()
      $("#id_"+id+"_container_moral").show()
  }
};

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

  if (confirm('¿Está seguro de eliminar el registro?') == true) {
      $.ajax({
          url : url,
          type : "POST",
          success : function(json) {
            $("#borrar-registro-" + id).hide()
            console.log(json);
          },
          error : function(xhr,errmsg,err) {
              console.log(xhr.status + ": " + xhr.responseText);
          }
      });
  } else {
      return false;
  }
};


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
              } else {
                  window.location.href =reload;
              }
          },
          error : function(xhr,errmsg,err) {

          }
      });

};