from .models import InfoPersonalFija
from import_export import resources, widgets, fields

class FijaResourceAdmin(resources.ModelResource):
    class Meta:
        model = InfoPersonalFija