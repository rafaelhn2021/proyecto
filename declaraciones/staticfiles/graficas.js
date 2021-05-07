//Funciones para dibujar graficas
function drawBarGraph(data, id) {
  var labels = data.labels; 
  var chartLabel = data.chartLabel; 
  var chartdata = data.chartdata; 
  var maxSuggested = data.total_usuario_activos;
  var extra_params = data.extra_params;
  var canvas = document.getElementById(id);
  var context = canvas.getContext('2d');
  context.clearRect(0, 0, canvas.width, canvas.height);

  var  myChart = new Chart(context, {
    type: 'bar', 
    data: {
      labels: labels, 
      datasets: [{
        label: chartLabel, 
        data: chartdata,
        backgroundColor: [ 
        "rgba(4, 96, 118, 0.2)", 
        "rgba(65, 117, 5, 0.2)", 
        "rgba(163, 179, 76, 0.2)", 
        "rgba(4, 96, 118, 0.2)", 
        "rgba(65, 117, 5, 0.2)"
        ], 
        borderColor: [
        "rgba(4, 96, 118, 1)", 
        "rgba(65, 117, 5, 1)", 
        "rgba(163, 179, 5, 1)", 
        "rgba(4, 96, 118, 1)", 
        "rgba(65, 117, 5, 1)"
        ], 
        borderWidth: 2
      }] 
    }, 
    options: {
      title:{
        display:true,
        text:"1.Usuarios registrados activos y cantidad de declaraciones creadas en "+extra_params[0]
      },
      scales: { 
        yAxes: [{ 
          ticks: { 
            beginAtZero: true,
            suggestedMax: maxSuggested
          }
        }] 
      }
    } 
  });
}
  
  function drawLineGraph(data, id) {
    var labels = data.lables_meses; 
    var chartLabel_dec = data.chartLabel; 
    var chartdata_dec = data.chartdata_datos_anuales_declaraciones; 

    var chartLabel_usu = data.chartLabel_usuario;
    var chartdata_usu = data.chartdata_datos_anuales_usuarios;

    var total_usuarios_declaraciones = data.total_usuarios_declaraciones
    var extra_params = data.extra_params;
    var canvas = document.getElementById(id);
    var context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);

    new Chart(context, {
      type: 'line',
      data: { 
        labels: labels, 
        datasets: [{ 
          label: chartLabel_dec, 
          borderColor: 'rgba(4, 96, 118, 1)', 
          backgroundColor: 'rgba(4, 96, 118, 0.2)', 
          data: chartdata_dec,
          borderWidth: 2
        },
        {
          label: chartLabel_usu,
          borderColor: 'rgba(65, 117, 5, 1)', 
          backgroundColor: 'rgba(65, 117, 5, 0.2)', 
          data: chartdata_usu,
          borderWidth: 2
        }] 
      }, 
      options: {
        title:{
          display:true,
          text:"2.Datos anuales de usuarios/declaraciones creadas en "+extra_params[0]
        },
        scales: { 
          yAxes: [{ 
            ticks: { 
              beginAtZero: true,
              stepSize: 1,
              suggestedMax: total_usuarios_declaraciones
            }
          }] 
        }
      }
    }); 
  }