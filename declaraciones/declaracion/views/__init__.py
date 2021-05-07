from .informacion_personal import (DeclaracionFormView, DatosCurricularesView,
                                   DatosEncargoActualView,
                                   ExperienciaLaboralView,
                                   ConyugeDependientesView,
                                   DatosCurricularesDelete,
                                   ExperienciaLaboralDeleteView,
                                   ConyugeDependientesDeleteView,DeclaracionFiscalFormView,
                                   DeclaracionFiscalDelete,listaMunicipios,DomiciliosViews,ParejaView,ParejaDeleteView)

from .intereses import (MembresiaView,
                        RepresentacionesActivasView,
                        SociosComercialesView,
                        ClientesPrincipalesView,
                        BeneficiosGratuitosView, ApoyosView,
                        MembresiaDeleteView,
                        SociosComercialesDeleteView,
                        ClientesPrincipalesDeleteView,
                        BeneficiosGratuitosDeleteView,
                        ApoyosDeleteView,
                        RepresentacionesActivasDeleteView)

from .pasivos import (DeudasView,DeudasDeleteView,PrestamoComodatoView,PrestamoComodatoDeleteView)
from .ingresos import IngresosDeclaracionView
from .activos import (BienesMueblesView, BienesInmueblesView,
                      MueblesNoRegistrablesView, InversionesView,
                      FideicomisosView,
                      BienesInmueblesDeleteView, BienesMueblesDeleteView,
                      MueblesNoRegistrablesDeleteView,
                      InversionesDeleteView,
                      FideicomisosDeleteView,listaTiposInversionesEspecificos)
from .declaracion import (DeclaracionView, DeclaracionDeleteView)
from .registro import (RegistroView,PerfilView,listaPuestos)
from .api import (RegistrosView)
from .confirmacion import (ConfirmarDeclaracionView,ConfirmacionAllinOne)
from .admin import (BusquedaDeclarantesFormView,
                    InfoDeclarantesFormView,
                    InfoDeclaracionFormView,
                    BusquedaDeclaracionesFormView,
                    BusquedaUsuariosFormView,
                    NuevoUsuariosOICFormView,
                    EliminarUsuarioFormView,
                    InfoUsuarioFormView,
                    EditarUsuarioFormView,
                    DescargarReportesView,
                    DeclaracionesGraficas,
                    DeclaracionesGraficasData,
                    RegistroDeclaranteFormView)