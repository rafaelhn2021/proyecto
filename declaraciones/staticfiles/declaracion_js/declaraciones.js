$(window).load(function(){
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
    console.log('upload-wrap',this);
        $('.image-upload-wrap').addClass('image-dropping');
    });
    $('.image-upload-wrap').bind('dragleave', function () {
        $('.image-upload-wrap').removeClass('image-dropping');
});