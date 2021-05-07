from .informacion_personal import (DeclaracionForm, InfoPersonalFijaForm,
                                   DomiciliosForm, InfoPersonalVarForm,
                                   ObservacionesForm, DatosCurricularesForm,
                                   DatosEncargoActualForm,
                                   ExperienciaLaboralForm,
                                   ConyugeDependientesForm,DeclaracionFiscalForm,ParejaForm)


from .intereses import (MembresiasForm,
                        RepresentacionesActivasForm,
                        SociosComercialesForm,
                        ClientesPrincipalesForm,
                        BeneficiosGratuitosForm, ApoyosForm)

from .pasivos import (DeudasForm,PrestamoComodatoForm)

from .ingresos import IngresosDeclaracionForm

from .activos import (BienesMueblesForm, BienesInmueblesForm,
                      MueblesNoRegistrablesForm, InversionesForm,
                      FideicomisosForm,
                      BienesPersonasForm,
                      ActivosBienesForm)

from .registro import (RegistroForm,CambioEntePublicoForm)
from .admin import (BusquedaDeclaracionForm,BusquedaUsuariosForm,RegistroUsuarioOICForm,
                    BusquedaDeclaranteForm,RegistroUsuarioDeclaranteForm,BusquedaDeclaracionExtForm,
                    BusquedaGraficasForm)
from .confirmacion import ConfirmacionForm
