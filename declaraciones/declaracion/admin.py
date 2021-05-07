from .models import InfoPersonalFija
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from import_export import resources, widgets, fields
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin,ExportMixin
from import_export.formats import base_formats


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email','is_active','is_staff')

class UserAdmin(ImportExportModelAdmin, UserAdmin):
    """
    Class UserAdmin utliza librera para exportar e importar datos de un modelo a un excel
    """
    resource_class = UserResource
    pass

class FijaResourceAdmin(resources.ModelResource):
    class Meta:
        model = InfoPersonalFija

class adminFija(ImportExportModelAdmin):
    resource_class = FijaResourceAdmin
    list_display = ('nombre_completo','cat_puestos','usuario')
    exclude = ['owner','puesto', 'usuario', 'nombre_ente_publico', 
               'fecha_nacimiento','curp','cat_ente_publico',
               'cat_entidades_federativas','cat_pais',
               'otro_ente', 'sended']

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(InfoPersonalFija, adminFija)